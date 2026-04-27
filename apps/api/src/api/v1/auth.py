"""
Authentication endpoints
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from src.core.tenant import get_current_tenant
from src.models.tenant import Tenant
from src.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    current_tier: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    current_tier: str
    subscription_status: str
    total_leads: int
    total_clients: int


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _resolve_tenant(db: AsyncSession, slug: str) -> Tenant:
    """Look up Tenant by its slug (tenants.tenant_id). Raise 400 if missing."""
    result = await db.execute(select(Tenant).where(Tenant.tenant_id == slug))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        logger.error("auth tenant_not_found slug=%s", slug)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown tenant '{slug}'. Run migrations / seed default tenants "
                "or pass an existing tenant via X-Tenant-ID header."
            ),
        )
    return tenant


def _build_token_response(user: User) -> TokenResponse:
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": str(user.id),
            "tier": user.current_tier,
            "tenant": str(user.tenant_id),
        }
    )
    refresh = create_refresh_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh,
        expires_in=settings.JWT_EXPIRES_IN * 24 * 3600,
        user=UserPublic(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            current_tier=user.current_tier,
        ),
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    request: Request,
    tenant_slug: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    logger.info(
        "auth.register email=%s tenant=%s ip=%s",
        user_data.email, tenant_slug, _client_ip(request),
    )

    tenant = await _resolve_tenant(db, tenant_slug)

    result = await db.execute(
        select(User).where(
            User.email == user_data.email,
            User.tenant_id == tenant.id,
        )
    )
    if result.scalar_one_or_none():
        logger.warning(
            "auth.register conflict email=%s tenant=%s", user_data.email, tenant_slug,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        tenant_id=tenant.id,
        current_tier="start",
        subscription_status="trial",
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(
        "auth.register success user_id=%s email=%s tenant=%s",
        new_user.id, new_user.email, tenant_slug,
    )
    return _build_token_response(new_user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    request: Request,
    tenant_slug: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Login with email/password (JSON)."""
    logger.info(
        "auth.login attempt email=%s tenant=%s ip=%s",
        payload.email, tenant_slug, _client_ip(request),
    )

    tenant = await _resolve_tenant(db, tenant_slug)

    result = await db.execute(
        select(User).where(
            User.email == payload.email,
            User.tenant_id == tenant.id,
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning(
            "auth.login failed email=%s reason=%s",
            payload.email,
            "no_user" if not user else "bad_password",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.subscription_status == "expired":
        logger.warning("auth.login expired email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription expired. Please renew.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info("auth.login success user_id=%s email=%s", user.id, user.email)
    return _build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Issue a new access/refresh token pair from a valid refresh token."""
    decoded = decode_token(payload.refresh_token, settings.REFRESH_TOKEN_SECRET)

    if decoded.get("type") != "refresh":
        logger.warning("auth.refresh wrong_token_type sub=%s", decoded.get("sub"))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = decoded.get("user_id")
    if not user_id:
        logger.warning("auth.refresh missing_user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("auth.refresh user_not_found user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    logger.info("auth.refresh success user_id=%s", user.id)
    return _build_token_response(user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user info."""
    user_id = current_user.get("user_id")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("auth.me user_not_found user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        current_tier=user.current_tier,
        subscription_status=user.subscription_status,
        total_leads=user.total_leads,
        total_clients=user.total_clients,
    )
