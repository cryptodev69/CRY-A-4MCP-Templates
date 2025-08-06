"""Database configuration and session management.

This module provides database connection setup, session management,
and database initialization for the URL mapping service.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models.url_mappings import Base


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./url_mappings.db"
)

# SQLite-specific configuration for foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Create engine with appropriate configuration
if "sqlite" in DATABASE_URL:
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        poolclass=StaticPool,
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
    )
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def create_tables():
    """Create all database tables.
    
    This function creates all tables defined in the models.
    It's safe to call multiple times as it only creates missing tables.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables.
    
    WARNING: This will delete all data! Only use for testing or reset.
    """
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session.
    
    This function provides a database session that automatically
    handles cleanup and error rollback.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a new database session.
    
    Returns:
        Database session (must be closed manually)
    """
    return SessionLocal()


def init_db():
    """Initialize the database.
    
    Creates all tables and performs any necessary setup.
    """
    create_tables()
    print("Database initialized successfully")


def reset_db():
    """Reset the database.
    
    WARNING: This will delete all data!
    """
    drop_tables()
    create_tables()
    print("Database reset successfully")


class DatabaseManager:
    """Database manager for handling connections and transactions."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_session(self) -> Session:
        """Create a new database session."""
        return self.SessionLocal()
    
    def init_database(self):
        """Initialize database tables."""
        create_tables()
    
    def reset_database(self):
        """Reset database (drop and recreate tables)."""
        reset_db()
    
    def health_check(self) -> bool:
        """Check if database connection is healthy.
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self.create_session() as session:
                session.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information.
        
        Returns:
            Dictionary with connection details
        """
        return {
            "url": DATABASE_URL,
            "driver": self.engine.driver,
            "pool_size": getattr(self.engine.pool, 'size', None),
            "max_overflow": getattr(self.engine.pool, 'max_overflow', None),
            "echo": self.engine.echo
        }


# Global database manager instance
db_manager = DatabaseManager()