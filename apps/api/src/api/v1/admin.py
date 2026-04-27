"""
Admin API endpoints
Tenant-scoped admin tools (tenants, users, subscriptions overview).
Access is restricted to users with role == "admin".
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List
import uuid
import logging

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.tenant import get_current_tenant
from src.models.user import User
from src.models.tenant import Tenant

router = APIRouter()
logger = logging.getLogger(__name__)


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/health")
async def admin_health(current_user: dict = Depends(require_admin)) -> Dict[str, Any]:
    return {"status": "ok", "actor": current_user.get("user_id")}


@router.get("/tenants")
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
) -> List[Dict[str, Any]]:
    result = await db.execute(select(Tenant))
    tenants = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "tenant_id": t.tenant_id,
            "name": t.name,
            "specialization": t.specialization,
            "status": t.status,
        }
        for t in tenants
    ]


@router.get("/users")
async def list_users(
    tenant_id: str = Depends(get_current_tenant),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
) -> List[Dict[str, Any]]:
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    result = await db.execute(
        select(User)
        .where(User.tenant_id == tenant.id)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "current_tier": u.current_tier,
            "subscription_status": getattr(u, "subscription_status", None),
        }
        for u in users
    ]


@router.get("/stats")
async def tenant_stats(
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
) -> Dict[str, Any]:
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    total_users = await db.scalar(
        select(func.count(User.id)).where(User.tenant_id == tenant.id)
    )
    by_tier = await db.execute(
        select(User.current_tier, func.count(User.id))
        .where(User.tenant_id == tenant.id)
        .group_by(User.current_tier)
    )

    return {
        "tenant_id": tenant_id,
        "total_users": int(total_users or 0),
        "by_tier": {tier or "unknown": int(count) for tier, count in by_tier.all()},
    }
