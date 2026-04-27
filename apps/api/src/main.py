"""
FishFlow API - Main Entry Point
FastAPI application with multi-tenant support
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.api.v1 import (
    admin,
    analytics,
    audit,
    auth,
    brand,
    content,
    funnel,
    marathon,
)
from src.core.config import settings
from src.core.database import close_db, init_db
from src.core.tenant import TenantMiddleware
from src.services.ai_service import AIService

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format=(
        "%(asctime)s %(levelname)-7s %(name)s "
        "[req=%(request_id)s tenant=%(tenant_id)s] %(message)s"
    ),
)


class ContextFilter(logging.Filter):
    """Inject default request_id/tenant_id so the formatter never crashes."""

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "tenant_id"):
            record.tenant_id = "-"
        return True


for _handler in logging.getLogger().handlers:
    _handler.addFilter(ContextFilter())

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FishFlow API environment=%s", settings.ENVIRONMENT)
    await init_db()
    app.state.ai_service = AIService()
    await app.state.ai_service.initialize()
    logger.info("FishFlow API started")
    yield
    logger.info("Shutting down FishFlow API")
    await close_db()
    await app.state.ai_service.shutdown()
    logger.info("FishFlow API stopped")


app = FastAPI(
    title="FishFlow API",
    description="AI Assistant for Experts - Multi-tenant Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    started = time.perf_counter()

    extra = {
        "request_id": request_id,
        "tenant_id": getattr(request.state, "tenant_id", "-"),
    }

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.exception(
            "%s %s -> 500 in %sms",
            request.method,
            request.url.path,
            elapsed_ms,
            extra=extra,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
            headers={"x-request-id": request_id},
        )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    extra["tenant_id"] = getattr(request.state, "tenant_id", extra["tenant_id"])
    log = logger.warning if response.status_code >= 500 else (
        logger.info if response.status_code >= 400 else logger.debug
    )
    log(
        "%s %s -> %s in %sms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        extra=extra,
    )
    response.headers["x-request-id"] = request_id
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-request-id"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.add_middleware(TenantMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0", "env": settings.ENVIRONMENT}


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
        reload=settings.DEBUG,
    )
