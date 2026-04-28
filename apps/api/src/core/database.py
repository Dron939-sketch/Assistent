"""
Database connection and session management.

On startup we ensure schema exists (Base.metadata.create_all) and seed
the three default tenants (nutrition / psychology / tarot) if the
tenants table is empty. This makes the API self-bootstrapping on Render
where running `psql \i ...` from packages/database is awkward.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings

logger = logging.getLogger(__name__)

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


def get_async_database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


DEFAULT_TENANTS = [
    {
        "tenant_id": "nutrition",
        "name": "NutroPult",
        "specialization": "nutrition",
        "config": {
            "tier_features": {
                "start": ["auto_funnel"],
                "pro": ["audit_vk", "post_generator"],
                "expert": ["marathon_builder"],
            }
        },
        "branding": {"primary_color": "#2E7D32"},
        "ai_config": {"model": "gpt-4-turbo-preview"},
    },
    {
        "tenant_id": "psychology",
        "name": "PsyFlow",
        "specialization": "psychology",
        "config": {
            "tier_features": {
                "start": ["auto_funnel"],
                "pro": ["audit_vk", "post_generator"],
                "expert": ["marathon_builder"],
            }
        },
        "branding": {"primary_color": "#4A90E2"},
        "ai_config": {"model": "gpt-4-turbo-preview"},
    },
    {
        "tenant_id": "tarot",
        "name": "TarologBot",
        "specialization": "tarot",
        "config": {
            "tier_features": {
                "start": ["auto_funnel"],
                "pro": ["audit_vk", "post_generator"],
                "expert": ["marathon_builder"],
            }
        },
        "branding": {"primary_color": "#9C27B0"},
        "ai_config": {"model": "gpt-4-turbo-preview"},
    },
]


async def _bootstrap_schema_and_seed(engine: AsyncEngine) -> None:
    """Create tables (if missing) and seed default tenants (if empty)."""
    # Importing the package registers every model class on Base.metadata.
    import src.models  # noqa: F401

    from src.models.tenant import Tenant
    from src.models.user import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verified (create_all)")

    factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        result = await session.execute(select(Tenant).limit(1))
        if result.scalar_one_or_none() is None:
            for spec in DEFAULT_TENANTS:
                session.add(Tenant(status="active", **spec))
            await session.commit()
            logger.info(
                "Seeded default tenants: %s",
                ", ".join(t["tenant_id"] for t in DEFAULT_TENANTS),
            )
        else:
            logger.debug("Tenants already present, skipping seed")


async def init_db():
    """Initialize database connection pool and bootstrap schema."""
    global _engine, _session_factory

    database_url = get_async_database_url()
    logger.info("Connecting to database: %s", database_url.split("@")[-1])

    _engine = create_async_engine(
        database_url,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    try:
        if settings.SKIP_DB_BOOTSTRAP:
            logger.info(
                "SKIP_DB_BOOTSTRAP is set; skipping schema create_all and tenant seed"
            )
        else:
            await _bootstrap_schema_and_seed(_engine)
    except Exception:
        logger.exception("Database bootstrap failed; the API will keep running but writes may fail")

    logger.info("Database connection pool created")


async def close_db():
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("Database connection pool closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if not _session_factory:
        raise RuntimeError("Database not initialized")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    if not _session_factory:
        raise RuntimeError("Database not initialized")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
