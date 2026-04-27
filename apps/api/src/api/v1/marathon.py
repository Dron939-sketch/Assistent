"""
Marathon API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.tenant import get_current_tenant
from src.models.marathon import Marathon, MarathonParticipant, MarathonDay
from src.services.ai_service import AIService
from src.services.marathon_service import MarathonService

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic schemas
class MarathonGenerateRequest(BaseModel):
    """Request to generate marathon structure"""
    name: str
    theme: str
    duration_days: int = Field(5, ge=3, le=30)
    audience: str
    pain_points: List[str]
    desired_outcome: str
    offer_after: Optional[str] = None
    platform: str = "telegram"
    is_free: bool = True
    price: Optional[float] = None


class MarathonCreate(BaseModel):
    name: str
    description: str
    duration_days: int
    structure: List[Dict]  # days with topics, tasks, bonuses
    platform: str = "telegram"
    is_free: bool = True
    price: Optional[float] = None
    welcome_message: Optional[str] = None
    completion_message: Optional[str] = None
    upsell_message: Optional[str] = None
    upsell_link: Optional[str] = None
    starts_at: Optional[datetime] = None


class MarathonUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    starts_at: Optional[datetime] = None
    upsell_message: Optional[str] = None
    upsell_link: Optional[str] = None


class MarathonResponse(BaseModel):
    id: str
    name: str
    description: str
    duration_days: int
    structure: List[Dict]
    platform: str
    is_free: bool
    price: Optional[float]
    status: str
    participants_count: int
    completed_count: int
    conversion_count: int
    starts_at: Optional[datetime]
    created_at: datetime


class MarathonGenerateResponse(BaseModel):
    name: str
    description: str
    duration_days: int
    structure: List[Dict]
    welcome_message: str
    completion_message: str
    upsell_message: str


class ParticipantRegister(BaseModel):
    name: str
    contact: str  # phone, telegram, email
    source: Optional[str] = None


class ParticipantResponse(BaseModel):
    id: str
    name: str
    contact: str
    current_day: int
    status: str
    completed_days: List[int]
    created_at: datetime


class HomeworkSubmit(BaseModel):
    participant_id: str
    day_number: int
    content: str
    files: Optional[List[str]] = None


class HomeworkResponse(BaseModel):
    score: int
    feedback: str
    is_correct: bool
    next_task: Optional[str] = None


class MarathonStats(BaseModel):
    total_participants: int
    active_participants: int
    completed_participants: int
    dropped_participants: int
    conversion_rate: float
    average_completion_day: float
    retention_by_day: Dict[int, int]


# Helper function to check tier access
def check_tier_access(current_tier: str, required_feature: str) -> bool:
    tier_features = {
        "start": ["auto_funnel", "auto_reply", "lead_collection"],
        "pro": ["auto_funnel", "auto_reply", "lead_collection", "audit_vk", 
                "content_plan", "post_generator", "case_generator", "leverage_point"],
        "expert": ["auto_funnel", "auto_reply", "lead_collection", "audit_vk",
                   "content_plan", "post_generator", "case_generator", "leverage_point",
                   "marathon_builder", "auto_homework_check", "brand_story", 
                   "uniqueness_analysis", "trust_audit", "landing_builder"]
    }
    return required_feature in tier_features.get(current_tier, [])


# ============================================
# Marathon generation endpoints
# ============================================

@router.post("/generate", response_model=MarathonGenerateResponse)
async def generate_marathon(
    request: MarathonGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate complete marathon structure using AI
    """
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "marathon_builder"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Marathon builder is available on Expert plan only. Please upgrade."
        )
    
    user_id = current_user.get("user_id")
    
    # Get user for personalization
    from src.models.user import User
    user_result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = user_result.scalar_one_or_none()
    
    # Generate marathon structure via AI
    ai_service = AIService()
    result = await ai_service.generate_marathon(
        theme=request.theme,
        duration_days=request.duration_days,
        audience=request.audience,
        pain_points=request.pain_points,
        desired_outcome=request.desired_outcome,
        offer_after=request.offer_after,
        voice_style=user.voice_style if user else None,
        specialization=current_user.get("specialization", "nutrition")
    )
    
    return MarathonGenerateResponse(
        name=request.name,
        description=result.get("description", f"Марафон «{request.theme}» за {request.duration_days} дней"),
        duration_days=request.duration_days,
        structure=result.get("structure", []),
        welcome_message=result.get("welcome_message", "Добро пожаловать на марафон!"),
        completion_message=result.get("completion_message", "Поздравляю с завершением марафона!"),
        upsell_message=result.get("upsell_message", "Хотите продолжить? Запишитесь на консультацию")
    )


@router.post("/", response_model=MarathonResponse)
async def create_marathon(
    request: MarathonCreate,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Create a new marathon from generated structure"""
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "marathon_builder"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Marathon builder is available on Expert plan only."
        )
    
    user_id = current_user.get("user_id")
    
    # Calculate end date
    starts_at = request.starts_at or datetime.utcnow() + timedelta(days=7)
    ends_at = starts_at + timedelta(days=request.duration_days)
    
    marathon = Marathon(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        name=request.name,
        description=request.description,
        duration_days=request.duration_days,
        structure=request.structure,
        platform=request.platform,
        is_free=request.is_free,
        price=request.price,
        welcome_message=request.welcome_message,
        completion_message=request.completion_message,
        upsell_message=request.upsell_message,
        upsell_link=request.upsell_link,
        starts_at=starts_at,
        ends_at=ends_at,
        status="draft"
    )
    
    db.add(marathon)
    await db.commit()
    await db.refresh(marathon)
    
    # Generate individual days
    marathon_service = MarathonService()
    await marathon_service.generate_days(marathon.id, request.structure, db)
    
    return MarathonResponse(
        id=str(marathon.id),
        name=marathon.name,
        description=marathon.description,
        duration_days=marathon.duration_days,
        structure=marathon.structure,
        platform=marathon.platform,
        is_free=marathon.is_free,
        price=float(marathon.price) if marathon.price else None,
        status=marathon.status,
        participants_count=marathon.participants_count,
        completed_count=marathon.completed_count,
        conversion_count=marathon.conversion_count,
        starts_at=marathon.starts_at,
        created_at=marathon.created_at
    )


@router.get("/", response_model=List[MarathonResponse])
async def list_marathons(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """List all marathons for current user"""
    
    user_id = current_user.get("user_id")
    
    query = select(Marathon).where(Marathon.user_id == uuid.UUID(user_id))
    
    if status_filter:
        query = query.where(Marathon.status == status_filter)
    
    query = query.order_by(Marathon.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    marathons = result.scalars().all()
    
    return [
        MarathonResponse(
            id=str(m.id),
            name=m.name,
            description=m.description,
            duration_days=m.duration_days,
            structure=m.structure,
            platform=m.platform,
            is_free=m.is_free,
            price=float(m.price) if m.price else None,
            status=m.status,
            participants_count=m.participants_count,
            completed_count=m.completed_count,
            conversion_count=m.conversion_count,
            starts_at=m.starts_at,
            created_at=m.created_at
        )
        for m in marathons
    ]


@router.get("/{marathon_id}", response_model=MarathonResponse)
async def get_marathon(
    marathon_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get marathon by ID"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(Marathon).where(
            Marathon.id == uuid.UUID(marathon_id),
            Marathon.user_id == uuid.UUID(user_id)
        )
    )
    marathon = result.scalar_one_or_none()
    
    if not marathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marathon not found")
    
    return MarathonResponse(
        id=str(marathon.id),
        name=marathon.name,
        description=marathon.description,
        duration_days=marathon.duration_days,
        structure=marathon.structure,
        platform=marathon.platform,
        is_free=marathon.is_free,
        price=float(marathon.price) if marathon.price else None,
        status=marathon.status,
        participants_count=marathon.participants_count,
        completed_count=marathon.completed_count,
        conversion_count=marathon.conversion_count,
        starts_at=marathon.starts_at,
        created_at=marathon.created_at
    )


@router.put("/{marathon_id}", response_model=MarathonResponse)
async def update_marathon(
    marathon_id: str,
    request: MarathonUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update marathon settings"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(Marathon).where(
            Marathon.id == uuid.UUID(marathon_id),
            Marathon.user_id == uuid.UUID(user_id)
        )
    )
    marathon = result.scalar_one_or_none()
    
    if not marathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marathon not found")
    
    if request.name:
        marathon.name = request.name
    if request.description:
        marathon.description = request.description
    if request.status:
        marathon.status = request.status
    if request.starts_at:
        marathon.starts_at = request.starts_at
        marathon.ends_at = request.starts_at + timedelta(days=marathon.duration_days)
    if request.upsell_message:
        marathon.upsell_message = request.upsell_message
    if request.upsell_link:
        marathon.upsell_link = request.upsell_link
    
    await db.commit()
    await db.refresh(marathon)
    
    return MarathonResponse(
        id=str(marathon.id),
        name=marathon.name,
        description=marathon.description,
        duration_days=marathon.duration_days,
        structure=marathon.structure,
        platform=marathon.platform,
        is_free=marathon.is_free,
        price=float(marathon.price) if marathon.price else None,
        status=marathon.status,
        participants_count=marathon.participants_count,
        completed_count=marathon.completed_count,
        conversion_count=marathon.conversion_count,
        starts_at=marathon.starts_at,
        created_at=marathon.created_at
    )


@router.delete("/{marathon_id}")
async def delete_marathon(
    marathon_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete marathon"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(Marathon).where(
            Marathon.id == uuid.UUID(marathon_id),
            Marathon.user_id == uuid.UUID(user_id)
        )
    )
    marathon = result.scalar_one_or_none()
    
    if not marathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marathon not found")
    
    await db.delete(marathon)
    await db.commit()
    
    return {"message": "Marathon deleted successfully"}


@router.post("/{marathon_id}/publish")
async def publish_marathon(
    marathon_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publish marathon (change status to active)"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(Marathon).where(
            Marathon.id == uuid.UUID(marathon_id),
            Marathon.user_id == uuid.UUID(user_id)
        )
    )
    marathon = result.scalar_one_or_none()
    
    if not marathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marathon not found")
    
    if marathon.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Marathon already published")
    
    marathon.status = "active"
    if not marathon.starts_at:
        marathon.starts_at = datetime.utcnow() + timedelta(days=7)
        marathon.ends_at = marathon.starts_at + timedelta(days=marathon.duration_days)
    
    await db.commit()
    
    # Create registration landing page link
    from src.config import settings
    registration_link = f"{settings.APP_URL}/marathon/{marathon_id}/register"
    
    return {
        "message": "Marathon published successfully",
        "registration_link": registration_link
    }


# ============================================
# Participant management
# ============================================

@router.post("/{marathon_id}/register", response_model=ParticipantResponse)
async def register_participant(
    marathon_id: str,
    request: ParticipantRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Register a new participant for marathon"""
    
    # Get marathon
    result = await db.execute(
        select(Marathon).where(Marathon.id == uuid.UUID(marathon_id))
    )
    marathon = result.scalar_one_or_none()
    
    if not marathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marathon not found")
    
    if marathon.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Marathon is not active")
    
    # Check if already registered
    existing = await db.execute(
        select(MarathonParticipant).where(
            MarathonParticipant.marathon_id == uuid.UUID(marathon_id),
            MarathonParticipant.contact == request.contact
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already registered")
    
    # Create participant
    participant = MarathonParticipant(
        marathon_id=uuid.UUID(marathon_id),
        name=request.name,
        contact=request.contact,
        source=request.source,
        status="active",
        current_day=1
    )
    
    db.add(participant)
    marathon.participants_count += 1
    await db.commit()
    await db.refresh(participant)
    
    # Send welcome message
    background_tasks.add_task(
        send_welcome_message,
        participant_id=str(participant.id),
        marathon_id=marathon_id
    )
    
    return ParticipantResponse(
        id=str(participant.id),
        name=participant.name,
        contact=participant.contact,
        current_day=participant.current_day,
        status=participant.status,
        completed_days=participant.completed_days or [],
        created_at=participant.created_at
    )


@router.get("/{marathon_id}/participants", response_model=List[ParticipantResponse])
async def list_participants(
    marathon_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None
):
    """List all participants for marathon"""
    
    user_id = current_user.get("user_id")
    
    # Verify ownership
    marathon_result = await db.execute(
        select(Marathon).where(
            Marathon.id == uuid.UUID(marathon_id),
            Marathon.user_id == uuid.UUID(user_id)
        )
    )
    if not marathon_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marathon not found")
    
    query = select(MarathonParticipant).where(
        MarathonParticipant.marathon_id == uuid.UUID(marathon_id)
    )
    
    if status_filter:
        query = query.where(MarathonParticipant.status == status_filter)
    
    result = await db.execute(query)
    participants = result.scalars().all()
    
    return [
        ParticipantResponse(
            id=str(p.id),
            name=p.name,
            contact=p.contact,
            current_day=p.current_day,
            status=p.status,
            completed_days=p.completed_days or [],
            created_at=p.created_at
        )
        for p in participants
    ]


# ============================================
# Homework and AI checking
# ============================================

@router.post("/homework/submit", response_model=HomeworkResponse)
async def submit_homework(
    request: HomeworkSubmit,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit homework for AI checking"""
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "auto_homework_check"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auto homework check is available on Expert plan only."
        )
    
    # Get participant
    result = await db.execute(
        select(MarathonParticipant).where(
            MarathonParticipant.id == uuid.UUID(request.participant_id)
        )
    )
    participant = result.scalar_one_or_none()
    
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    
    # Get marathon day content
    day_result = await db.execute(
        select(MarathonDay).where(
            MarathonDay.marathon_id == participant.marathon_id,
            MarathonDay.day_number == request.day_number
        )
    )
    day = day_result.scalar_one_or_none()
    
    # Get the task description
    task_description = day.task_description if day else "Выполните задание"
    
    # Get marathon for context
    marathon_result = await db.execute(
        select(Marathon).where(Marathon.id == participant.marathon_id)
    )
    marathon = marathon_result.scalar_one_or_none()
    
    # Check homework with AI
    ai_service = AIService()
    check_result = await ai_service.check_homework(
        task=task_description,
        submission=request.content,
        marathon_theme=marathon.name if marathon else "",
        specialization=current_user.get("specialization", "nutrition")
    )
    
    # Record submission
    submissions = participant.homework_submissions or []
    submissions.append({
        "day": request.day_number,
        "content": request.content,
        "score": check_result.get("score", 0),
        "feedback": check_result.get("feedback", ""),
        "submitted_at": datetime.utcnow().isoformat()
    })
    participant.homework_submissions = submissions
    
    scores = participant.homework_scores or []
    scores.append({
        "day": request.day_number,
        "score": check_result.get("score", 0)
    })
    participant.homework_scores = scores
    
    # Check if all days completed
    completed_days = participant.completed_days or []
    if request.day_number not in completed_days and check_result.get("score", 0) >= 50:
        completed_days.append(request.day_number)
        participant.completed_days = completed_days
        participant.current_day = max(participant.current_day, request.day_number + 1)
        
        # Check if marathon completed
        if len(completed_days) >= marathon.duration_days:
            participant.status = "completed"
            
            # Send upsell message
            background_tasks.add_task(
                send_upsell_message,
                participant_id=str(participant.id),
                marathon=marathon
            )
    
    await db.commit()
    
    return HomeworkResponse(
        score=check_result.get("score", 0),
        feedback=check_result.get("feedback", "Попробуйте ещё раз!"),
        is_correct=check_result.get("score", 0) >= 50,
        next_task=day.task_description if day else None
    )


@router.get("/{marathon_id}/stats", response_model=MarathonStats)
async def get_marathon_stats(
    marathon_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get marathon statistics"""
    
    user_id = current_user.get("user_id")
    
    # Verify ownership
    marathon_result = await db.execute(
        select(Marathon).where(
            Marathon.id == uuid.UUID(marathon_id),
            Marathon.user_id == uuid.UUID(user_id)
        )
    )
    marathon = marathon_result.scalar_one_or_none()
    
    if not marathon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marathon not found")
    
    # Get participants stats
    result = await db.execute(
        select(
            func.count(MarathonParticipant.id).filter(
                MarathonParticipant.status == "active"
            ).label("active"),
            func.count(MarathonParticipant.id).filter(
                MarathonParticipant.status == "completed"
            ).label("completed"),
            func.count(MarathonParticipant.id).filter(
                MarathonParticipant.status == "dropped"
            ).label("dropped"),
            func.count(MarathonParticipant.id).filter(
                MarathonParticipant.converted_to_client == True
            ).label("converted")
        ).where(MarathonParticipant.marathon_id == uuid.UUID(marathon_id))
    )
    stats = result.one()
    
    # Calculate retention by day
    retention_result = await db.execute(
        select(
            func.unnest(MarathonParticipant.completed_days).label("day"),
            func.count().label("count")
        ).where(MarathonParticipant.marathon_id == uuid.UUID(marathon_id))
        .group_by("day")
        .order_by("day")
    )
    retention = {row.day: row.count for row in retention_result}
    
    conversion_rate = (stats.converted / marathon.participants_count * 100) if marathon.participants_count > 0 else 0
    
    return MarathonStats(
        total_participants=marathon.participants_count,
        active_participants=stats.active or 0,
        completed_participants=stats.completed or 0,
        dropped_participants=stats.dropped or 0,
        conversion_rate=round(conversion_rate, 2),
        average_completion_day=0,  # Could calculate
        retention_by_day=retention
    )


# ============================================
# Background tasks
# ============================================

async def send_welcome_message(participant_id: str, marathon_id: str):
    """Send welcome message to participant"""
    async with get_db_context() as db:
        # Get participant and marathon
        participant_result = await db.execute(
            select(MarathonParticipant).where(MarathonParticipant.id == uuid.UUID(participant_id))
        )
        participant = participant_result.scalar_one()
        
        marathon_result = await db.execute(
            select(Marathon).where(Marathon.id == uuid.UUID(marathon_id))
        )
        marathon = marathon_result.scalar_one()
        
        # Send via Telegram or VK
        from src.services.telegram_service import TelegramService
        from src.services.vk_service import VKService
        
        if marathon.platform == "telegram":
            service = TelegramService()
            await service.send_message(
                chat_id=participant.contact,
                text=marathon.welcome_message or f"Добро пожаловать на марафон {marathon.name}! Готовы начать?"
            )
        else:
            # VK
            service = VKService()
            # Need peer_id extraction logic
            pass


async def send_upsell_message(participant_id: str, marathon: Marathon):
    """Send upsell message after marathon completion"""
    async with get_db_context() as db:
        participant_result = await db.execute(
            select(MarathonParticipant).where(MarathonParticipant.id == uuid.UUID(participant_id))
        )
        participant = participant_result.scalar_one()
        
        # Mark as converted if upsell was used
        participant.converted_to_client = True
        participant.converted_value = float(marathon.price) if marathon.price else 0
        participant.converted_at = datetime.utcnow()
        
        # Update marathon stats
        marathon.conversion_count += 1
        if marathon.price:
            marathon.conversion_revenue = (marathon.conversion_revenue or 0) + (marathon.price or 0)
        
        await db.commit()
