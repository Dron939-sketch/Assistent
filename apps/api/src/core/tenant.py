"""
Multi-tenant middleware and utilities
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts tenant from request:
    1. Subdomain: nutrition.fishflow.ru -> tenant = nutrition
    2. Header: X-Tenant-ID: nutrition
    3. Query param: ?tenant=nutrition
    4. Default: from config
    """
    
    async def dispatch(self, request: Request, call_next):
        tenant_id = self._extract_tenant(request)
        
        # Store tenant in request state
        request.state.tenant_id = tenant_id
        
        # Add to headers for downstream services
        request.headers.__dict__["_list"].append(
            (b"x-tenant-id", tenant_id.encode())
        )
        
        logger.debug(f"Request tenant: {tenant_id}, path: {request.url.path}")
        
        response = await call_next(request)
        return response
    
    def _extract_tenant(self, request: Request) -> str:
        """Extract tenant ID from various sources"""
        
        # 1. From header
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            return tenant_header
        
        # 2. From query parameter
        tenant_query = request.query_params.get("tenant")
        if tenant_query:
            return tenant_query
        
        # 3. From subdomain
        host = request.headers.get("host", "")
        # Check for subdomain pattern: {tenant}.fishflow.ru
        if ".fishflow.ru" in host:
            subdomain = host.split(".fishflow.ru")[0]
            if subdomain and subdomain not in ["www", "app", "api", "admin"]:
                return subdomain
        
        # 4. Default tenant
        from src.core.config import settings
        default_tenant = getattr(settings, "DEFAULT_TENANT", "nutrition")
        return default_tenant


async def get_current_tenant(request: Request) -> str:
    """Dependency to get current tenant"""
    return request.state.tenant_id


class TenantContext:
    """Context manager for tenant-specific operations"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
    
    async def __aenter__(self):
        import asyncio
        self.token = asyncio.current_task()
        # Store tenant in context var
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
