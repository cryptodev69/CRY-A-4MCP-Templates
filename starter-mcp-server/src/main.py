"""Main FastAPI application for URL mapping service.

This module sets up the FastAPI application with all necessary middleware,
routers, and configuration for the URL mapping service.
"""

import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import start_http_server
import uvicorn

from .database import init_db, db_manager
from .cry_a_4mcp.api.endpoints.url_mappings import setup_url_mapping_routes
from .exceptions import URLMappingBaseError
from .cry_a_4mcp.api.endpoints.extractors import router as extractors_router
from .cry_a_4mcp.api.endpoints.test_url import router as test_url_router
from .cry_a_4mcp.api.endpoints.url_configurations import setup_url_configuration_routes
from .cry_a_4mcp.storage.url_configuration_db import URLConfigurationDatabase
from .cry_a_4mcp.storage.url_mappings_db import URLMappingsDatabase


# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'table', 'status']
)


# Initialize databases globally
url_config_db = URLConfigurationDatabase()
url_mappings_db = URLMappingsDatabase()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting URL Mapping Service...")
    
    # Initialize database
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise
    
    # Initialize URL Configuration Database
    try:
        await url_config_db.initialize()
        print("URL Configuration Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize URL Configuration Database: {e}")
        raise
    
    # Initialize URL Mappings Database
    try:
        await url_mappings_db.initialize()
        print("URL Mappings Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize URL Mappings Database: {e}")
        raise
    
    # Start Prometheus metrics server if enabled
    if os.getenv("ENABLE_METRICS", "true").lower() == "true":
        metrics_port = int(os.getenv("METRICS_PORT", "8001"))
        start_http_server(metrics_port)
        print(f"Metrics server started on port {metrics_port}")
    
    print("URL Mapping Service started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down URL Mapping Service...")

# Create FastAPI application
app = FastAPI(
    title="URL Mapping Service",
    description="RESTful API for managing URL mappings with multiple extractor support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Trusted host middleware for security
if os.getenv("TRUSTED_HOSTS"):
    trusted_hosts = os.getenv("TRUSTED_HOSTS").split(",")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )


# Request timing and metrics middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request timing and metrics collection."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response


# Include routers
app.include_router(extractors_router)

# Include test URL router with /api prefix
app.include_router(test_url_router, prefix="/api")

# Setup URL mapping routes with database dependencies
url_mappings_router = setup_url_mapping_routes(url_mappings_db, url_config_db)
app.include_router(url_mappings_router)

# Setup URL configuration routes with database dependency
url_config_router = setup_url_configuration_routes(url_config_db)
app.include_router(url_config_router)


# Root endpoint
@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "URL Mapping Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", summary="Health check")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Database health check
    try:
        db_healthy = db_manager.health_check()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "connection_info": db_manager.get_connection_info()
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


# Metrics endpoint
@app.get("/metrics", summary="Prometheus metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Global exception handler
@app.exception_handler(URLMappingBaseError)
async def url_mapping_exception_handler(request: Request, exc: URLMappingBaseError):
    """Handle URL mapping specific exceptions."""
    status_code_map = {
        "URLMappingNotFoundError": 404,
        "URLMappingValidationError": 422,
        "URLMappingDuplicateError": 409,
        "DatabaseError": 500,
        "ExtractorNotFoundError": 404,
        "URLConfigNotFoundError": 404,
        "RateLimitExceededError": 429,
        "PermissionDeniedError": 403,
        "InvalidParameterError": 400
    }
    
    status_code = status_code_map.get(exc.error_code, 500)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "timestamp": time.time()
        }
    )


# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": time.time()
        }
    )


# Configuration endpoint
@app.get("/config", summary="Service configuration")
async def get_config():
    """Get service configuration (non-sensitive)."""
    return {
        "database": {
            "type": "sqlite" if "sqlite" in os.getenv("DATABASE_URL", "") else "other",
            "echo": os.getenv("SQL_DEBUG", "false").lower() == "true"
        },
        "cors": {
            "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*").split(",")
        },
        "metrics": {
            "enabled": os.getenv("ENABLE_METRICS", "true").lower() == "true",
            "port": int(os.getenv("METRICS_PORT", "8001"))
        }
    }


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "src.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "4000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )