"""
Content generation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.tenant import get_current_tenant
from src.models.content import ContentGeneration, ContentCalendar
from src.services.ai_service import AIService
from src.services.vk_service import VKService

router = APIRouter()


# Pydantic schemas
class ContentGenerateRequest(BaseModel):
    type: str = Field(..., description="post, reply, marathon_day, story, case, checklist")
    topic: Optional[str] = Field(None, description="Topic or subject")
    context: Optional[str] = Field(None, description="Additional context")
    tone: Optional[str] = Field(None, description="friendly, expert, strict, warm")
    length: Optional[str] = Field(None, description="short, medium, long")


class ContentRegenerateRequest(BaseModel):
    generation_id: str
    feedback: Optional[str] = Field(None, description="What to change")


class PostGenerateRequest(BaseModel):
    topic: str
    content_type: str = Field("post", description="post, case, checklist")
    include_hashtags: bool = True
    include_questions: bool = True


class CaseGenerateRequest(BaseModel):
    problem: str
    solution: str
    result: str
    client_type: Optional[str] = None
    duration: Optional[str] = None


class ContentResponse(BaseModel):
    id: str
    type: str
    topic: Optional[str]
    output_text: str
    output_metadata: Dict[str, Any]
    status: str
    created_at: datetime


class SchedulePostRequest(BaseModel):
    content_id: str
    scheduled_for: datetime
    timezone: str = "Europe/Moscow"


class CalendarItemResponse(BaseModel):
    id: str
    title: str
    content: Optional[str]
    content_type: str
    scheduled_for: datetime
    status: str


# Helper function to check tier access
def check_tier_access(current_tier: str, required_feature: str) -> bool:
    """Check if user has access to feature based on tier"""
    tier_features = {
        "start": ["auto_funnel", "auto_reply", "lead_collection"],
        "pro": ["auto_funnel", "auto_reply", "lead_collection", "audit_vk", 
                "content_plan", "post_generator", "case_generator", "leverage_point"],
        "expert": ["auto_funnel", "auto_reply", "lead_collection", "audit_vk",
                   "content_plan", "post_generator", "case_generator", "leverage_point",
                   "marathon_builder", "brand_story", "uniqueness_analysis", 
                   "trust_audit", "landing_builder"]
    }
    return required_feature in tier_features.get(current_tier, [])


# Endpoints
@router.post("/generate/post", response_model=ContentResponse)
async def generate_post(
    request: PostGenerateRequest,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Generate a VK post on given topic"""
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "post_generator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Post generator is available on Pro and Expert plans. Please upgrade."
        )
    
    user_id = current_user.get("user_id")
    
    # Create generation record
    generation = ContentGeneration(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        type=request.content_type,
        topic=request.topic,
        input_text=request.topic,
        status="processing"
    )
    
    db.add(generation)
    await db.commit()
    await db.refresh(generation)
    
    # Generate content via AI
    ai_service = AIService()
    
    # Get user context for personalization
    from src.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = user_result.scalar_one_or_none()
    
    result = await ai_service.generate_post(
        topic=request.topic,
        content_type=request.content_type,
        voice_style=user.voice_style if user else None,
        uniqueness=user.uniqueness if user else None,
        specialization=current_user.get("specialization", "nutrition"),
        include_hashtags=request.include_hashtags,
        include_questions=request.include_questions
    )
    
    # Update generation record
    generation.output_text = result.get("text", "")
    generation.output_metadata = {
        "title": result.get("title", ""),
        "hashtags": result.get("hashtags", []),
        "questions": result.get("questions", []),
        "suggested_image_prompt": result.get("image_prompt")
    }
    generation.status = "completed"
    generation.tokens_used = result.get("tokens_used", 0)
    
    await db.commit()
    await db.refresh(generation)
    
    return ContentResponse(
        id=str(generation.id),
        type=generation.type,
        topic=generation.topic,
        output_text=generation.output_text,
        output_metadata=generation.output_metadata,
        status=generation.status,
        created_at=generation.created_at
    )


@router.post("/generate/case", response_model=ContentResponse)
async def generate_case(
    request: CaseGenerateRequest,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Generate a client case study post"""
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "case_generator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Case generator is available on Pro and Expert plans. Please upgrade."
        )
    
    user_id = current_user.get("user_id")
    
    # Create generation record
    generation = ContentGeneration(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        type="case",
        topic=f"Кейс: {request.problem[:50]}...",
        input_text=f"Problem: {request.problem}\nSolution: {request.solution}\nResult: {request.result}",
        status="processing"
    )
    
    db.add(generation)
    await db.commit()
    await db.refresh(generation)
    
    # Generate case via AI
    ai_service = AIService()
    
    # Get user context
    from src.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = user_result.scalar_one_or_none()
    
    result = await ai_service.generate_case_study(
        problem=request.problem,
        solution=request.solution,
        result=request.result,
        client_type=request.client_type,
        duration=request.duration,
        voice_style=user.voice_style if user else None
    )
    
    # Update generation
    generation.output_text = result.get("text", "")
    generation.output_metadata = {
        "title": result.get("title", ""),
        "before_after": result.get("before_after"),
        "hashtags": result.get("hashtags", [])
    }
    generation.status = "completed"
    
    await db.commit()
    
    return ContentResponse(
        id=str(generation.id),
        type=generation.type,
        topic=generation.topic,
        output_text=generation.output_text,
        output_metadata=generation.output_metadata,
        status=generation.status,
        created_at=generation.created_at
    )


@router.post("/generate/reply", response_model=ContentResponse)
async def generate_reply(
    message: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Generate an auto-reply to a client message (objection handling)"""
    
    user_id = current_user.get("user_id")
    
    # Create generation record
    generation = ContentGeneration(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        type="reply",
        input_text=message,
        status="processing"
    )
    
    db.add(generation)
    await db.commit()
    
    # Generate reply via AI
    ai_service = AIService()
    
    # Get user context
    from src.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = user_result.scalar_one_or_none()
    
    result = await ai_service.generate_reply(
        message=message,
        voice_style=user.voice_style if user else None,
        specialization=current_user.get("specialization", "nutrition")
    )
    
    # Update generation
    generation.output_text = result.get("reply", "")
    generation.output_metadata = {"strategy": result.get("strategy", "")}
    generation.status = "completed"
    
    await db.commit()
    
    return ContentResponse(
        id=str(generation.id),
        type="reply",
        topic=None,
        output_text=generation.output_text,
        output_metadata=generation.output_metadata,
        status=generation.status,
        created_at=generation.created_at
    )


@router.post("/regenerate", response_model=ContentResponse)
async def regenerate_content(
    request: ContentRegenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db)
):
    """Regenerate content based on feedback"""
    
    user_id = current_user.get("user_id")
    
    # Get original generation
    result = await db.execute(
        select(ContentGeneration).where(
            ContentGeneration.id == uuid.UUID(request.generation_id),
            ContentGeneration.user_id == uuid.UUID(user_id)
        )
    )
    original = result.scalar_one_or_none()
    
    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    
    # Save previous version
    versions = original.versions or []
    versions.append({
        "text": original.output_text,
        "metadata": original.output_metadata,
        "created_at": datetime.utcnow().isoformat()
    })
    
    # Regenerate with feedback
    ai_service = AIService()
    
    if original.type == "post":
        new_result = await ai_service.generate_post(
            topic=original.topic or original.input_text,
            content_type=original.type,
            feedback=request.feedback,
            previous_version=original.output_text
        )
    else:
        new_result = await ai_service.regenerate(
            original_type=original.type,
            original_input=original.input_text,
            feedback=request.feedback,
            previous_version=original.output_text
        )
    
    # Update generation
    original.output_text = new_result.get("text", "")
    original.output_metadata = new_result.get("metadata", {})
    original.versions = versions
    original.tokens_used = new_result.get("tokens_used", 0)
    
    await db.commit()
    
    return ContentResponse(
        id=str(original.id),
        type=original.type,
        topic=original.topic,
        output_text=original.output_text,
        output_metadata=original.output_metadata,
        status=original.status,
        created_at=original.created_at
    )


@router.post("/schedule", response_model=CalendarItemResponse)
async def schedule_post(
    request: SchedulePostRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a generated post to VK"""
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "post_generator"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scheduling is available on Pro and Expert plans. Please upgrade."
        )
    
    user_id = current_user.get("user_id")
    
    # Get generation
    result = await db.execute(
        select(ContentGeneration).where(
            ContentGeneration.id == uuid.UUID(request.content_id),
            ContentGeneration.user_id == uuid.UUID(user_id)
        )
    )
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if already scheduled
    existing = await db.execute(
        select(ContentCalendar).where(
            ContentCalendar.generation_id == generation.id,
            ContentCalendar.status == "scheduled"
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content already scheduled"
        )
    
    # Create calendar entry
    calendar_item = ContentCalendar(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        title=generation.topic or f"{generation.type} post",
        content=generation.output_text,
        content_type=generation.type,
        scheduled_for=request.scheduled_for,
        timezone=request.timezone,
        generation_id=generation.id,
        status="scheduled"
    )
    
    db.add(calendar_item)
    await db.commit()
    await db.refresh(calendar_item)
    
    return CalendarItemResponse(
        id=str(calendar_item.id),
        title=calendar_item.title,
        content=calendar_item.content,
        content_type=calendar_item.content_type,
        scheduled_for=calendar_item.scheduled_for,
        status=calendar_item.status
    )


@router.get("/calendar", response_model=List[CalendarItemResponse])
async def get_calendar(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get scheduled content calendar"""
    
    user_id = current_user.get("user_id")
    
    query = select(ContentCalendar).where(
        ContentCalendar.user_id == uuid.UUID(user_id),
        ContentCalendar.status == "scheduled"
    )
    
    if start_date:
        query = query.where(ContentCalendar.scheduled_for >= start_date)
    if end_date:
        query = query.where(ContentCalendar.scheduled_for <= end_date)
    
    query = query.order_by(ContentCalendar.scheduled_for)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return [
        CalendarItemResponse(
            id=str(item.id),
            title=item.title,
            content=item.content,
            content_type=item.content_type,
            scheduled_for=item.scheduled_for,
            status=item.status
        )
        for item in items
    ]
