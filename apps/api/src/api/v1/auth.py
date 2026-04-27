"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from src.core.database import get_db
from src.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    get_current_user
)
from src.models.user import User
from src.core.tenant import get_current_tenant

router = APIRouter()


# Pydantic schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    current_tier: str
    subscription_status: str
    total_leads: int
    total_clients: int


# Endpoints
@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    
    # Check if user exists
    result = await db.execute(
        select(User).where(
            User.email == user_data.email,
            User.tenant_id == tenant_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        tenant_id=tenant_id,
        current_tier="start",
        subscription_status="trial"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": new_user.email, "user_id": str(new_user.id), "tier": new_user.current_tier}
    )
    refresh_token = create_refresh_token(
        data={"sub": new_user.email, "user_id": str(new_user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=7 * 24 * 3600  # 7 days in seconds
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with email/password (OAuth2 form)"""
    
    # Find user
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check subscription
    if user.subscription_status == "expired":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription expired. Please renew."
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "tier": user.current_tier, "tenant": user.tenant_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    
    # Update last login
    from datetime import datetime, timezone
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=7 * 24 * 3600
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Get new access token using refresh token"""
    from src.core.security import decode_token
    
    payload = decode_token(refresh_token, settings.REFRESH_TOKEN_SECRET)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "tier": user.current_tier, "tenant": user.tenant_id}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=7 * 24 * 3600
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user info"""
    
    user_id = current_user.get("user_id")
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        current_tier=user.current_tier,
        subscription_status=user.subscription_status,
        total_leads=user.total_leads,
        total_clients=user.total_clients
    )
