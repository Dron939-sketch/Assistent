"""
Database utilities for worker (sync)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Database URL (sync version)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/fishflow")

# Convert async URL to sync if needed
if "+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """Get database session for sync operations"""
    return SessionLocal()


def close_db_connections():
    """Close all database connections"""
    engine.dispose()
