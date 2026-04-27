"""
FishFlow API - Main Entry Point
FastAPI application with multi-tenant support
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from src.core.config import settings
from src.core.database import init_db, close_db
from src.core.tenant import TenantMiddleware
from src.api.v1 import auth, audit, content, marathon, funnel, analytics, brand, admin
from src.services.ai_service import AIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Starting FishFlow API...")
    
    # Initialize database connection pool
    await init_db()
    
    # Initialize AI service
    app.state.ai_service = AIService()
    await app.state.ai_service.initialize()
    
    logger.info("FishFlow API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FishFlow API...")
    await close_db()
    await app.state.ai_service.shutdown()
    logger.info("FishFlow API stopped")


# Create FastAPI application
app = FastAPI(
    title="FishFlow API",
    description="AI Assistant for Experts - Multi-tenant Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Tenant middleware (extracts tenant from domain/header)
app.add_middleware(TenantMiddleware)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


# API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(marathon.router, prefix="/api/v1/marathon", tags=["marathon"])
app.include_router(funnel.router, prefix="/api/v1/funnel", tags=["funnel"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(brand.router, prefix="/api/v1/brand", tags=["brand"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
