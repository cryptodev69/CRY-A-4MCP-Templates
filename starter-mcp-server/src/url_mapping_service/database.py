"""Database configuration and session management for URL Mapping Service.

This module provides database connection management, session handling,
and database health checks.
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import Settings, get_settings
from .exceptions import DatabaseError

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and session manager."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize database manager.
        
        Args:
            settings: Application settings. If None, uses global settings.
        """
        self.settings = settings or get_settings()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize database engine and session factory."""
        try:
            # Configure engine based on database type
            if self.settings.database_url.startswith("sqlite"):
                # SQLite specific configuration
                self.engine = create_engine(
                    self.settings.database_url,
                    echo=self.settings.database_echo,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": self.settings.db_pool_timeout,
                    },
                    poolclass=StaticPool,
                )
            else:
                # PostgreSQL/MySQL configuration
                self.engine = create_engine(
                    self.settings.database_url,
                    echo=self.settings.database_echo,
                    pool_size=self.settings.db_pool_size,
                    max_overflow=self.settings.db_max_overflow,
                    pool_timeout=self.settings.db_pool_timeout,
                    pool_recycle=self.settings.db_pool_recycle,
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database engine initialized: {self.settings.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise DatabaseError(f"Database initialization failed: {e}") from e
    
    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            from .models import URLMapping  # Import here to avoid circular imports
            URLMapping.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise DatabaseError(f"Table creation failed: {e}") from e
    
    def drop_tables(self) -> None:
        """Drop all database tables."""
        try:
            from .models import URLMapping  # Import here to avoid circular imports
            URLMapping.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise DatabaseError(f"Table drop failed: {e}") from e
    
    def health_check(self) -> bool:
        """Check database connection health.
        
        Returns:
            bool: True if database is healthy, False otherwise.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup.
        
        Yields:
            Session: SQLAlchemy database session.
            
        Raises:
            DatabaseError: If session creation or operation fails.
        """
        if not self.SessionLocal:
            raise DatabaseError("Database not initialized")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(f"Database operation failed: {e}") from e
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected session error: {e}")
            raise DatabaseError(f"Unexpected database error: {e}") from e
        finally:
            session.close()
    
    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance.
    
    Returns:
        DatabaseManager: Global database manager.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions.
    
    Yields:
        Session: SQLAlchemy database session.
    """
    db_manager = get_database_manager()
    with db_manager.get_session() as session:
        yield session


def initialize_database() -> None:
    """Initialize database and create tables."""
    db_manager = get_database_manager()
    db_manager.create_tables()
    logger.info("Database initialized successfully")


def close_database() -> None:
    """Close database connections."""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None


# Database utilities
def execute_raw_sql(sql: str, params: Optional[dict] = None) -> list:
    """Execute raw SQL query.
    
    Args:
        sql: SQL query string.
        params: Query parameters.
        
    Returns:
        list: Query results.
        
    Raises:
        DatabaseError: If query execution fails.
    """
    db_manager = get_database_manager()
    try:
        with db_manager.get_session() as session:
            result = session.execute(text(sql), params or {})
            return result.fetchall()
    except Exception as e:
        logger.error(f"Raw SQL execution failed: {e}")
        raise DatabaseError(f"SQL execution failed: {e}") from e


def backup_database(backup_path: str) -> None:
    """Create database backup.
    
    Args:
        backup_path: Path to backup file.
        
    Raises:
        DatabaseError: If backup creation fails.
    """
    settings = get_settings()
    
    if not settings.backup_enabled:
        logger.warning("Database backup is disabled")
        return
    
    try:
        # Implementation depends on database type
        if settings.database_url.startswith("sqlite"):
            import shutil
            from urllib.parse import urlparse
            
            # Extract database file path from URL
            parsed = urlparse(settings.database_url)
            db_path = parsed.path.lstrip("/")
            
            # Copy SQLite file
            shutil.copy2(db_path, backup_path)
            logger.info(f"SQLite database backed up to: {backup_path}")
        else:
            # For PostgreSQL/MySQL, use pg_dump/mysqldump
            logger.warning("Backup for PostgreSQL/MySQL not implemented")
            
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise DatabaseError(f"Backup failed: {e}") from e