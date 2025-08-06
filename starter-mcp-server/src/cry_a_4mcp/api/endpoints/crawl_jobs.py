"""Crawl Jobs API Endpoints for CRY-A-4MCP Platform.

This module provides comprehensive REST API endpoints for managing crawl jobs within
the CRY-A-4MCP cryptocurrency data collection platform. It handles the complete
lifecycle of crawl jobs including creation, monitoring, execution control, and cleanup.

Key Features:
    - CRUD operations for crawl job management
    - Pagination and filtering for large job datasets
    - Real-time job status tracking and updates
    - Job execution control (start/stop/pause)
    - Integration with URL configuration database
    - Async crawler system integration
    - Comprehensive error handling and logging

API Endpoints:
    GET /api/crawl-jobs - List all crawl jobs with pagination
    GET /api/crawl-jobs/{job_id} - Get specific crawl job details
    POST /api/crawl-jobs - Create new crawl job
    PUT /api/crawl-jobs/{job_id} - Update existing crawl job
    DELETE /api/crawl-jobs/{job_id} - Delete crawl job
    POST /api/crawl-jobs/{job_id}/start - Start job execution
    POST /api/crawl-jobs/{job_id}/stop - Stop job execution

Typical Usage:
    ```python
    # Setup routes with dependencies
    router = setup_crawl_job_routes(url_db, crawler)
    app.include_router(router)
    
    # Create a new crawl job
    job_data = CrawlJobCreate(
        name="Daily News Crawl",
        crawler_id=1,
        schedule="0 9 * * *"
    )
    response = await client.post("/api/crawl-jobs", json=job_data.dict())
    ```

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

# Standard library imports
from typing import List, Optional  # Type hints for function signatures
from datetime import datetime  # Timestamp handling for job lifecycle events
import logging  # Structured logging for monitoring and debugging

# Third-party imports
from fastapi import APIRouter, HTTPException, Query  # FastAPI framework components

# Internal imports
from ...storage.url_configuration_db import URLConfigurationDatabase  # Database operations
from ...crypto_crawler.crawler import GenericAsyncCrawler  # Crawler integration
from ..models import CrawlJobCreate, CrawlJobUpdate, CrawlJobResponse  # Pydantic models

# FastAPI router configuration
# Prefix groups all endpoints under /api/crawl-jobs namespace
# Tags enable automatic API documentation grouping
router = APIRouter(prefix="/api/crawl-jobs", tags=["Crawl Jobs"])

# Module-level logger for tracking API operations and debugging
# Uses the module name for easy log filtering and monitoring
logger = logging.getLogger(__name__)


def setup_crawl_job_routes(url_db: URLConfigurationDatabase, crawler: GenericAsyncCrawler):
    """Setup crawl job routes with database and crawler dependencies.
    
    This function configures all crawl job API endpoints with their required dependencies.
    It uses dependency injection to provide database and crawler instances to each endpoint,
    enabling proper separation of concerns and testability.
    
    Args:
        url_db (URLConfigurationDatabase): Database instance for crawl job persistence
            and retrieval operations. Handles all CRUD operations for job data.
        crawler (GenericAsyncCrawler): Async crawler instance for job execution
            control and monitoring. Manages the actual crawling processes.
    
    Returns:
        APIRouter: Configured FastAPI router with all crawl job endpoints
            registered and ready for inclusion in the main application.
    
    Example:
        ```python
        # Initialize dependencies
        db = URLConfigurationDatabase(connection_string)
        crawler = GenericAsyncCrawler(config)
        
        # Setup routes
        router = setup_crawl_job_routes(db, crawler)
        
        # Include in main app
        app.include_router(router)
        ```
    
    Note:
        This function uses closure to capture the dependencies, allowing
        the endpoint handlers to access them without global state.
    """
    
    @router.get("", response_model=List[CrawlJobResponse])
    async def get_crawl_jobs(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Items per page"),
        status: Optional[str] = Query(None, description="Filter by status"),
        crawler_id: Optional[int] = Query(None, description="Filter by crawler ID")
    ):
        """Get all crawl jobs with pagination and filtering.
        
        Retrieves a paginated list of crawl jobs from the database with optional
        status and crawler ID filtering. This endpoint supports efficient data retrieval for
        large job datasets through page-based pagination.
        
        Args:
            page (int): Page number for pagination (1-based indexing).
                Must be >= 1. Defaults to 1 for first page.
            limit (int): Maximum number of jobs to return per page.
                Must be between 1-100. Defaults to 10 for performance.
            status (Optional[str]): Filter jobs by their current status.
                Common values: 'pending', 'running', 'completed', 'failed'.
            crawler_id (Optional[int]): Filter jobs by specific crawler ID.
                Useful for viewing jobs from a particular crawler instance.
        
        Returns:
            List[CrawlJobResponse]: List of crawl job objects matching the criteria.
                Each job includes id, name, status, timestamps, and configuration.
        
        Raises:
            HTTPException: 500 if database operation fails or internal error occurs.
        
        Example:
            GET /api/crawl-jobs?page=3&limit=20&status=running&crawler_id=5
            Returns page 3 (jobs 41-60) that are currently running for crawler 5.
        """
        try:
            # Log the request for monitoring and debugging purposes
            logger.info(f"Retrieving crawl jobs: page={page}, limit={limit}, status={status}, crawler_id={crawler_id}")
            
            # Calculate offset for database pagination
            # Convert 1-based page number to 0-based offset
            offset = (page - 1) * limit
            
            # Query database with pagination parameters
            # The database layer handles SQL optimization and result mapping
            jobs = await url_db.get_crawl_jobs_paginated(offset=offset, limit=limit)
            
            # Apply status filter if provided
            # Filter in-memory for flexibility, could be moved to DB for performance
            if status:
                jobs = [j for j in jobs if j.get('status') == status]
                logger.debug(f"Applied status filter '{status}', {len(jobs)} jobs remaining")
            
            # Apply crawler ID filter if provided
            # Useful for isolating jobs from specific crawler instances
            if crawler_id:
                jobs = [j for j in jobs if j.get('crawler_id') == crawler_id]
                logger.debug(f"Applied crawler_id filter '{crawler_id}', {len(jobs)} jobs remaining")
            
            # Log successful retrieval for monitoring
            logger.debug(f"Successfully retrieved {len(jobs)} crawl jobs")
            
            return jobs
        except Exception as e:
            # Log the full error for debugging while returning safe message to client
            logger.error(f"Error getting crawl jobs: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Internal server error while retrieving crawl jobs"
            )
    
    @router.get("/{job_id}", response_model=CrawlJobResponse)
    async def get_crawl_job(job_id: int):
        """Get a specific crawl job by ID.
        
        Retrieves detailed information about a single crawl job identified by its
        unique ID. This endpoint provides complete job details including configuration,
        status, timestamps, and execution history.
        
        Args:
            job_id (int): Unique identifier of the crawl job to retrieve.
                Must be a positive integer corresponding to an existing job.
        
        Returns:
            CrawlJobResponse: Complete crawl job object with all details including:
                - Basic info: id, name, description
                - Configuration: crawler_id, schedule, parameters
                - Status: current state, progress, timestamps
                - History: creation, last run, next scheduled run
        
        Raises:
            HTTPException: 404 if job with specified ID doesn't exist.
            HTTPException: 500 if database operation fails or internal error occurs.
        
        Example:
            GET /api/crawl-jobs/123
            Returns complete details for crawl job with ID 123.
        """
        try:
            # Log the request for monitoring and debugging
            logger.info(f"Retrieving crawl job with ID: {job_id}")
            
            # Query database for the specific job
            # Database layer handles ID validation and data mapping
            job = await url_db.get_crawl_job(job_id)
            
            # Check if job exists and return appropriate response
            if not job:
                logger.warning(f"Crawl job not found: {job_id}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Crawl job with ID {job_id} not found"
                )
            
            # Log successful retrieval
            logger.debug(f"Successfully retrieved crawl job {job_id}: {job.get('name', 'Unknown')}")
            
            return job
        except HTTPException:
            # Re-raise HTTP exceptions (like 404) without modification
            # These are expected errors that should reach the client
            raise
        except Exception as e:
            # Log unexpected errors for debugging while returning safe message
            logger.error(f"Error retrieving crawl job {job_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Internal server error while retrieving crawl job"
            )
    
    @router.post("", response_model=CrawlJobResponse)
    async def create_crawl_job(job: CrawlJobCreate):
        """Create a new crawl job.
        
        Creates a new crawl job with the provided configuration. This endpoint
        validates the job data, assigns a unique ID, sets initial status, and
        persists the job to the database for future execution.
        
        Args:
            job (CrawlJobCreate): Crawl job creation data containing:
                - name: Human-readable job identifier
                - description: Optional job description
                - crawler_id: ID of crawler to use for execution
                - schedule: Cron expression for job scheduling
                - url_patterns: List of URL patterns to crawl
                - parameters: Additional crawler-specific configuration
        
        Returns:
            CrawlJobResponse: Created crawl job object with assigned ID,
                timestamps, and initial status set to 'pending'.
        
        Raises:
            HTTPException: 400 if job data validation fails.
            HTTPException: 500 if database operation fails or internal error occurs.
        
        Example:
            POST /api/crawl-jobs
            {
                "name": "Daily News Crawl",
                "crawler_id": 1,
                "schedule": "0 9 * * *",
                "url_patterns": ["https://news.example.com/*"]
            }
        """
        try:
            # Log the job creation request for monitoring
            logger.info(f"Creating new crawl job: {job.name}")
            
            # Convert Pydantic model to dictionary for database operations
            # This ensures proper serialization and validation
            job_data = job.dict()
            
            # Add creation timestamp and initial status
            # Use ISO format for consistent timestamp handling
            job_data['status'] = 'pending'
            job_data['created_at'] = datetime.utcnow().isoformat()
            
            # Create job in database with validation and ID assignment
            # Database layer handles uniqueness constraints and data integrity
            job_id = await url_db.create_crawl_job(job_data)
            
            # Retrieve the complete created job object for response
            # This ensures the client receives the full job data with assigned ID
            created_job = await url_db.get_crawl_job(job_id)
            
            # Log successful creation with assigned ID
            logger.info(f"Successfully created crawl job {job_id}: {job.name}")
            
            return created_job
        except ValueError as e:
            # Handle validation errors with specific client-friendly messages
            logger.warning(f"Validation error creating crawl job: {e}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid job data: {str(e)}"
            )
        except Exception as e:
            # Log unexpected errors for debugging while returning safe message
            logger.error(f"Error creating crawl job: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Internal server error while creating crawl job"
            )
    
    @router.put("/{job_id}", response_model=CrawlJobResponse)
    async def update_crawl_job(job_id: int, job: CrawlJobUpdate):
        """Update an existing crawl job.
        
        Updates an existing crawl job with new configuration data. This endpoint
        supports partial updates, allowing clients to modify only specific fields
        while preserving other job attributes.
        
        Args:
            job_id (int): Unique identifier of the crawl job to update.
                Must correspond to an existing job in the database.
            job (CrawlJobUpdate): Partial job data containing fields to update.
                Only provided fields will be modified, others remain unchanged.
                Supports: name, description, schedule, url_patterns, parameters, status.
        
        Returns:
            CrawlJobResponse: Updated crawl job object with modified fields
                and updated timestamp reflecting the change.
        
        Raises:
            HTTPException: 404 if job with specified ID doesn't exist.
            HTTPException: 400 if update data validation fails.
            HTTPException: 500 if database operation fails or internal error occurs.
        
        Example:
            PUT /api/crawl-jobs/123
            {
                "name": "Updated Job Name",
                "schedule": "0 12 * * *"
            }
            Updates only name and schedule, preserving other fields.
        """
        try:
            # Log the update request for monitoring
            logger.info(f"Updating crawl job {job_id}")
            
            # Check if job exists before attempting update
            # This prevents unnecessary database operations and provides clear error messages
            existing_job = await url_db.get_crawl_job(job_id)
            if not existing_job:
                logger.warning(f"Attempted to update non-existent crawl job: {job_id}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Crawl job with ID {job_id} not found"
                )
            
            # Convert update model to dictionary, excluding unset fields
            # This enables partial updates without overwriting existing data
            update_data = {k: v for k, v in job.dict().items() if v is not None}
            
            # Add update timestamp to track modification history
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Log the fields being updated for debugging
            logger.debug(f"Updating job {job_id} fields: {list(update_data.keys())}")
            
            # Perform the database update operation
            # Database layer handles field validation and data integrity
            success = await url_db.update_crawl_job(job_id, update_data)
            if not success:
                logger.warning(f"Database update failed for crawl job: {job_id}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Crawl job with ID {job_id} not found"
                )
            
            # Retrieve the updated job to return complete current state
            # This ensures the client receives the latest job data
            updated_job = await url_db.get_crawl_job(job_id)
            
            # Log successful update
            logger.info(f"Successfully updated crawl job {job_id}")
            
            return updated_job
        except HTTPException:
            # Re-raise HTTP exceptions (like 404) without modification
            # These are expected errors that should reach the client
            raise
        except ValueError as e:
            # Handle validation errors with specific client-friendly messages
            logger.warning(f"Validation error updating crawl job {job_id}: {e}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid update data: {str(e)}"
            )
        except Exception as e:
            # Log unexpected errors for debugging while returning safe message
            logger.error(f"Error updating crawl job {job_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Internal server error while updating crawl job"
            )
    
    @router.delete("/{job_id}")
    async def delete_crawl_job(job_id: int):
        """Delete a crawl job.
        
        Permanently removes a crawl job from the system. This operation is
        irreversible and will also clean up associated data such as crawl
        history, scheduled tasks, and temporary files.
        
        Args:
            job_id (int): Unique identifier of the crawl job to delete.
                Must correspond to an existing job in the database.
        
        Returns:
            dict: Success message confirming job deletion with timestamp.
        
        Raises:
            HTTPException: 404 if job with specified ID doesn't exist.
            HTTPException: 409 if job is currently running and cannot be deleted.
            HTTPException: 500 if database operation fails or internal error occurs.
        
        Example:
            DELETE /api/crawl-jobs/123
            Returns: {"message": "Crawl job deleted successfully", "deleted_at": "..."}
        
        Warning:
            This operation is permanent and cannot be undone. Ensure the job
            is not currently running before deletion.
        """
        try:
            # Log the deletion request for audit trail
            logger.info(f"Attempting to delete crawl job {job_id}")
            
            # Check if job exists before attempting deletion
            # This provides clear error messages and prevents unnecessary operations
            existing_job = await url_db.get_crawl_job(job_id)
            if not existing_job:
                logger.warning(f"Attempted to delete non-existent crawl job: {job_id}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Crawl job with ID {job_id} not found"
                )
            
            # Check if job is currently running to prevent unsafe deletion
            # Running jobs should be stopped before deletion to avoid data corruption
            if existing_job.get('status') == 'running':
                logger.warning(f"Attempted to delete running crawl job: {job_id}")
                raise HTTPException(
                    status_code=409,
                    detail=f"Cannot delete crawl job {job_id}: job is currently running. Stop the job first."
                )
            
            # Log job details before deletion for audit purposes
            job_name = existing_job.get('name', 'Unknown')
            logger.info(f"Deleting crawl job {job_id}: {job_name}")
            
            # Perform the database deletion operation
            # Database layer handles cascading deletes and referential integrity
            success = await url_db.delete_crawl_job(job_id)
            if not success:
                # This shouldn't happen if the existence check passed, but handle gracefully
                logger.error(f"Database deletion failed for existing crawl job: {job_id}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to delete crawl job due to database error"
                )
            
            # Log successful deletion with timestamp for audit trail
            deletion_time = datetime.utcnow().isoformat()
            logger.info(f"Successfully deleted crawl job {job_id}: {job_name} at {deletion_time}")
            
            return {
                "message": "Crawl job deleted successfully",
                "job_id": job_id,
                "deleted_at": deletion_time
            }
        except HTTPException:
            # Re-raise HTTP exceptions (like 404, 409) without modification
            # These are expected errors that should reach the client
            raise
        except Exception as e:
            # Log unexpected errors for debugging while returning safe message
            logger.error(f"Error deleting crawl job {job_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Internal server error while deleting crawl job"
            )
    
    @router.post("/{job_id}/start")
    async def start_crawl_job(job_id: int):
        """Start a crawl job.
        
        Initiates execution of a crawl job, transitioning it from pending/stopped
        state to running state. This endpoint validates job readiness, starts
        the crawler process, and updates the job status accordingly.
        
        Args:
            job_id (int): Unique identifier of the crawl job to start.
                Must correspond to an existing job that is not already running.
        
        Returns:
            dict: Success message with job start details and timestamp.
        
        Raises:
            HTTPException: 404 if job with specified ID doesn't exist.
            HTTPException: 409 if job is already running or in invalid state.
            HTTPException: 500 if crawler startup fails or internal error occurs.
        
        Example:
            POST /api/crawl-jobs/123/start
            Returns: {
                "message": "Crawl job started successfully",
                "job_id": 123,
                "started_at": "2024-01-15T10:30:00Z"
            }
        
        Note:
            The job must be in 'pending', 'stopped', or 'failed' state to be started.
            Running or completed jobs cannot be restarted without proper state reset.
        """
        try:
            # Log the start request for monitoring and debugging
            logger.info(f"Attempting to start crawl job {job_id}")
            
            # Check if job exists and retrieve current state
            # This ensures we have valid job data before attempting to start
            job = await url_db.get_crawl_job(job_id)
            if not job:
                logger.warning(f"Attempted to start non-existent crawl job: {job_id}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Crawl job with ID {job_id} not found"
                )
            
            # Validate job state before starting
            # Only certain states allow job startup to prevent conflicts
            current_status = job.get('status', 'unknown')
            if current_status == 'running':
                logger.warning(f"Attempted to start already running crawl job: {job_id}")
                raise HTTPException(
                    status_code=409,
                    detail=f"Crawl job {job_id} is already running"
                )
            
            # Check if job can be started based on current status
            if current_status not in ['pending', 'failed', 'stopped']:
                logger.warning(f"Attempted to start crawl job {job_id} in invalid state: {current_status}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Job cannot be started in current status: {current_status}"
                )
            
            # Check if job has valid configuration for execution
            if not job.get('crawler_id'):
                logger.warning(f"Attempted to start crawl job {job_id} without crawler configuration")
                raise HTTPException(
                    status_code=400,
                    detail=f"Crawl job {job_id} has no crawler configured"
                )
            
            # Log job details before starting
            job_name = job.get('name', 'Unknown')
            logger.info(f"Starting crawl job {job_id}: {job_name}")
            
            # Update job status and timestamp in database
            # This provides real-time status tracking for monitoring
            start_time = datetime.utcnow().isoformat()
            await url_db.update_crawl_job(job_id, {
                'status': 'running',
                'started_at': start_time,
                'updated_at': start_time
            })
            
            # TODO: Integrate with actual crawling system
            # The crawler.start_job(job_id) call will be added when crawler integration is complete
            # For now, the job status is updated to indicate it has been started
            
            # Log successful start
            logger.info(f"Successfully started crawl job {job_id}: {job_name} at {start_time}")
            
            return {
                "message": "Crawl job started successfully",
                "job_id": job_id,
                "job_name": job_name,
                "started_at": start_time
            }
        except HTTPException:
            # Re-raise HTTP exceptions (like 404, 409) without modification
            # These are expected errors that should reach the client
            raise
        except Exception as e:
            # Log unexpected errors for debugging while returning safe message
            logger.error(f"Error starting crawl job {job_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Internal server error while starting crawl job"
            )
    
    @router.post("/{job_id}/stop")
    async def stop_crawl_job(job_id: int):
        """Stop a running crawl job.
        
        Gracefully terminates a running crawl job, allowing it to complete
        current operations before stopping. This endpoint validates job state,
        signals the crawler to stop, and updates the job status accordingly.
        
        Args:
            job_id (int): Unique identifier of the crawl job to stop.
                Must correspond to an existing job that is currently running.
        
        Returns:
            dict: Success message with job stop details and timestamp.
        
        Raises:
            HTTPException: 404 if job with specified ID doesn't exist.
            HTTPException: 400 if job is not currently running.
            HTTPException: 500 if crawler stop fails or internal error occurs.
        
        Example:
            POST /api/crawl-jobs/123/stop
            Returns: {
                "message": "Crawl job stopped successfully",
                "job_id": 123,
                "stopped_at": "2024-01-15T10:45:00Z"
            }
        
        Note:
            This performs a graceful shutdown, allowing the crawler to finish
            processing current URLs before terminating. For immediate termination,
            use the force stop endpoint (if available).
        """
        try:
            # Log the stop request for monitoring and debugging
            logger.info(f"Attempting to stop crawl job {job_id}")
            
            # Check if job exists and retrieve current state
            # This ensures we have valid job data before attempting to stop
            job = await url_db.get_crawl_job(job_id)
            if not job:
                logger.warning(f"Attempted to stop non-existent crawl job: {job_id}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Crawl job with ID {job_id} not found"
                )
            
            # Validate job state before stopping
            # Only running jobs can be stopped to prevent invalid state transitions
            current_status = job.get('status', 'unknown')
            if current_status != 'running':
                logger.warning(f"Attempted to stop non-running crawl job {job_id}: {current_status}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Job is not currently running (status: {current_status})"
                )
            
            # Log job details before stopping
            job_name = job.get('name', 'Unknown')
            logger.info(f"Stopping crawl job {job_id}: {job_name}")
            
            # TODO: Integrate with actual crawling system to stop the job
            # The crawler.stop_job(job_id) call will be added when crawler integration is complete
            # This should signal the crawler to gracefully terminate the job
            
            # Update job status and timestamp in database
            # This provides real-time status tracking for monitoring
            stop_time = datetime.utcnow().isoformat()
            await url_db.update_crawl_job(job_id, {
                'status': 'stopped',
                'stopped_at': stop_time,
                'updated_at': stop_time
            })
            
            # Log successful stop
            logger.info(f"Successfully stopped crawl job {job_id}: {job_name} at {stop_time}")
            
            return {
                "message": "Crawl job stopped successfully",
                "job_id": job_id,
                "job_name": job_name,
                "stopped_at": stop_time
            }
        except HTTPException:
            # Re-raise HTTP exceptions (like 404, 400) without modification
            # These are expected errors that should reach the client
            raise
        except Exception as e:
            # Log unexpected errors for debugging while returning safe message
            logger.error(f"Error stopping crawl job {job_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail="Internal server error while stopping crawl job"
            )
    
    return router