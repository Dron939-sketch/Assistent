"""
Database utilities for worker (sync).

DATABASE_URL must be set via environment. We keep a localhost default for
developer convenience but refuse to start under ENVIRONMENT=production
without an explicit URL.
"""

import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").lower()
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    if ENVIRONMENT in {"production", "prod", "staging"}:
        raise RuntimeError(
            f"DATABASE_URL is required in {ENVIRONMENT} but is not set"
        )
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fishflow"
    logger.warning("DATABASE_URL not set; using local default")

# Convert async URL to sync if needed (asyncpg → psycopg)
if "+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.environ.get("WORKER_DB_POOL_SIZE", "5")),
    max_overflow=int(os.environ.get("WORKER_DB_MAX_OVERFLOW", "10")),
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """Get database session for sync operations."""
    return SessionLocal()


def close_db_connections() -> None:
    """Close all database connections."""
    engine.dispose()
