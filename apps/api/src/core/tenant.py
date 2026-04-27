"""
Multi-tenant middleware and utilities
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)

RESERVED_SUBDOMAINS = {"www", "app", "api", "admin"}


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Resolve current tenant from the request, in priority order:
      1. X-Tenant-ID header
      2. ?tenant=... query parameter
      3. {tenant}.fishflow.ru subdomain
      4. settings.DEFAULT_TENANT
    The result is stored in request.state.tenant_id.
    """

    async def dispatch(self, request: Request, call_next):
        tenant_id = self._extract_tenant(request)
        request.state.tenant_id = tenant_id
        logger.debug("Request tenant=%s path=%s", tenant_id, request.url.path)
        return await call_next(request)

    @staticmethod
    def _extract_tenant(request: Request) -> str:
        header = request.headers.get("X-Tenant-ID")
        if header:
            return header.strip()

        query = request.query_params.get("tenant")
        if query:
            return query.strip()

        host = request.headers.get("host", "").split(":", 1)[0]
        if host.endswith(".fishflow.ru"):
            subdomain = host[: -len(".fishflow.ru")]
            if subdomain and subdomain not in RESERVED_SUBDOMAINS:
                return subdomain

        return settings.DEFAULT_TENANT


async def get_current_tenant(request: Request) -> str:
    """FastAPI dependency to get current tenant id from request state."""
    return getattr(request.state, "tenant_id", settings.DEFAULT_TENANT)
