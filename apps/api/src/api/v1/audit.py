"""
VK Audit API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
import uuid

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.tenant import get_current_tenant
from src.models.audit import VKAudit, VKAuditDetail
from src.services.vk_service import VKService
from src.services.audit_service import AuditService
from src.services.ai_service import AIService

router = APIRouter()


# Pydantic schemas
class AuditRequest(BaseModel):
    vk_page_url: HttpUrl


class AuditCategoryScore(BaseModel):
    category: str
    score: int
    max_score: int
    issues: List[str]
    recommendations: List[str]


class AuditResponse(BaseModel):
    id: str
    vk_page_url: str
    vk_group_id: str
    score: int
    categories: List[AuditCategoryScore]
    recommendations: dict
    status: str
    created_at: datetime
    completed_at: Optional[datetime]


class AuditListResponse(BaseModel):
    id: str
    vk_page_url: str
    score: int
    status: str
    created_at: datetime


# Endpoints
@router.post("/vk", response_model=AuditResponse)
async def create_vk_audit(
    request: AuditRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new VK page audit
    """
    user_id = current_user.get("user_id")
    
    # Extract group ID from URL
    vk_service = VKService()
    group_id = vk_service.extract_group_id(str(request.vk_page_url))
    
    if not group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid VK page URL. Please provide a valid VK group or public page URL."
        )
    
    # Check feature access (tier check)
    # User must have 'audit_vk' feature (Pro or Expert tier)
    user_tier = current_user.get("tier", "start")
    if user_tier not in ["pro", "expert"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="VK Audit is available on Pro and Expert plans. Please upgrade."
        )
    
    # Create audit record
    audit = VKAudit(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        vk_page_url=str(request.vk_page_url),
        vk_group_id=group_id,
        status="pending",
        result={}
    )
    
    db.add(audit)
    await db.commit()
    await db.refresh(audit)
    
    # Run audit in background
    background_tasks.add_task(
        run_vk_audit,
        audit_id=str(audit.id),
        group_id=group_id,
        user_id=user_id
    )
    
    # Return initial response
    return AuditResponse(
        id=str(audit.id),
        vk_page_url=audit.vk_page_url,
        vk_group_id=audit.vk_group_id,
        score=0,
        categories=[],
        recommendations={},
        status="pending",
        created_at=audit.created_at,
        completed_at=None
    )


@router.get("/vk/{audit_id}", response_model=AuditResponse)
async def get_vk_audit(
    audit_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get audit results by ID
    """
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(VKAudit).where(
            VKAudit.id == uuid.UUID(audit_id),
            VKAudit.user_id == uuid.UUID(user_id)
        )
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    # Get category details
    details_result = await db.execute(
        select(VKAuditDetail).where(VKAuditDetail.audit_id == audit.id)
    )
    details = details_result.scalars().all()
    
    categories = []
    for detail in details:
        categories.append(AuditCategoryScore(
            category=detail.category,
            score=detail.score or 0,
            max_score=detail.max_score or 10,
            issues=detail.issues or [],
            recommendations=detail.recommendations or []
        ))
    
    return AuditResponse(
        id=str(audit.id),
        vk_page_url=audit.vk_page_url,
        vk_group_id=audit.vk_group_id,
        score=audit.score or 0,
        categories=categories,
        recommendations=audit.recommendations or {},
        status=audit.status,
        created_at=audit.created_at,
        completed_at=audit.completed_at
    )


@router.get("/vk", response_model=List[AuditListResponse])
async def list_vk_audits(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """
    List all audits for current user
    """
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(VKAudit)
        .where(VKAudit.user_id == uuid.UUID(user_id))
        .order_by(VKAudit.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    audits = result.scalars().all()
    
    return [
        AuditListResponse(
            id=str(a.id),
            vk_page_url=a.vk_page_url,
            score=a.score or 0,
            status=a.status,
            created_at=a.created_at
        )
        for a in audits
    ]


# Background task
async def run_vk_audit(audit_id: str, group_id: str, user_id: str):
    """
    Background task to run VK audit
    """
    from src.core.database import get_db_context
    from src.services.audit_service import AuditService
    
    async with get_db_context() as db:
        try:
            # Update status to processing
            await db.execute(
                update(VKAudit)
                .where(VKAudit.id == uuid.UUID(audit_id))
                .values(status="processing")
            )
            await db.commit()
            
            # Run audit
            audit_service = AuditService()
            result = await audit_service.audit_vk_page(group_id, user_id)
            
            # Calculate scores
            total_score = sum(cat["score"] for cat in result["categories"])
            max_score = sum(cat["max_score"] for cat in result["categories"])
            final_score = int((total_score / max_score) * 100) if max_score > 0 else 0
            
            # Update audit record
            await db.execute(
                update(VKAudit)
                .where(VKAudit.id == uuid.UUID(audit_id))
                .values(
                    status="completed",
                    score=final_score,
                    result=result,
                    recommendations=result.get("global_recommendations", {}),
                    completed_at=datetime.utcnow()
                )
            )
            
            # Insert category details
            for cat in result["categories"]:
                detail = VKAuditDetail(
                    audit_id=uuid.UUID(audit_id),
                    category=cat["category"],
                    score=cat["score"],
                    max_score=cat["max_score"],
                    issues=cat.get("issues", []),
                    recommendations=cat.get("recommendations", [])
                )
                db.add(detail)
            
            await db.commit()
            
        except Exception as e:
            # Update status to failed
            await db.execute(
                update(VKAudit)
                .where(VKAudit.id == uuid.UUID(audit_id))
                .values(
                    status="failed",
                    error_message=str(e)
                )
            )
            await db.commit()
