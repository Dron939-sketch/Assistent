"""
Auto funnel API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Request
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
from src.models.funnel import AutoFunnel, Lead, FunnelSession
from src.models.user import User
from src.services.ai_service import AIService
from src.services.vk_service import VKService

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic schemas
class FunnelCreate(BaseModel):
    name: str
    trigger_keywords: List[str] = Field(default=["дорого", "сколько стоит", "цена", "подумаю", "как записаться", "консультация"])
    flow_steps: Optional[List[Dict]] = None
    use_ai: bool = True
    custom_prompt: Optional[str] = None


class FunnelUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    trigger_keywords: Optional[List[str]] = None
    flow_steps: Optional[List[Dict]] = None
    use_ai: Optional[bool] = None
    custom_prompt: Optional[str] = None
    fallback_message: Optional[str] = None


class FunnelResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    trigger_keywords: List[str]
    flow_steps: List[Dict]
    use_ai: bool
    total_triggers: int
    total_converted: int
    total_leads: int
    created_at: datetime


class LeadResponse(BaseModel):
    id: str
    source: str
    name: Optional[str]
    contact: Optional[str]
    status: str
    conversation: List[Dict]
    booked_at: Optional[datetime]
    created_at: datetime


class LeadListResponse(BaseModel):
    id: str
    name: Optional[str]
    contact: Optional[str]
    status: str
    source: str
    created_at: datetime


class WebhookMessage(BaseModel):
    """VK Callback API message format"""
    type: str
    object: Dict[str, Any]
    group_id: int
    secret: Optional[str] = None


# Helper function to check tier access
def check_tier_access(current_tier: str, required_feature: str) -> bool:
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


# ============================================
# Funnel CRUD endpoints
# ============================================

@router.post("/funnels", response_model=FunnelResponse)
async def create_funnel(
    request: FunnelCreate,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db)
):
    """Create a new auto funnel"""
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "auto_funnel"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auto funnel is only available on paid plans. Please upgrade."
        )
    
    user_id = current_user.get("user_id")
    
    funnel = AutoFunnel(
        user_id=uuid.UUID(user_id),
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        name=request.name,
        trigger_keywords=request.trigger_keywords,
        flow_steps=request.flow_steps or [
            {"step": 1, "type": "message", "content": "Здравствуйте! Рада вашему вопросу.", "delay_minutes": 0},
            {"step": 2, "type": "ask_contact", "content": "Оставьте ваш телефон или Telegram, я пришлю подробную информацию", "delay_minutes": 0},
            {"step": 3, "type": "send_material", "content": "Вот мой гайд по [теме]. Надеюсь, будет полезен!", "delay_minutes": 0},
            {"step": 4, "type": "ask_booking", "content": "Готовы записаться на консультацию? Выберите удобное время", "delay_minutes": 1440}
        ],
        use_ai=request.use_ai,
        custom_prompt=request.custom_prompt
    )
    
    db.add(funnel)
    await db.commit()
    await db.refresh(funnel)
    
    return FunnelResponse(
        id=str(funnel.id),
        name=funnel.name,
        is_active=funnel.is_active,
        trigger_keywords=funnel.trigger_keywords,
        flow_steps=funnel.flow_steps,
        use_ai=funnel.use_ai,
        total_triggers=funnel.total_triggers,
        total_converted=funnel.total_converted,
        total_leads=funnel.total_leads,
        created_at=funnel.created_at
    )


@router.get("/funnels", response_model=List[FunnelResponse])
async def list_funnels(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all auto funnels"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(AutoFunnel)
        .where(AutoFunnel.user_id == uuid.UUID(user_id))
        .order_by(AutoFunnel.created_at.desc())
    )
    funnels = result.scalars().all()
    
    return [
        FunnelResponse(
            id=str(f.id),
            name=f.name,
            is_active=f.is_active,
            trigger_keywords=f.trigger_keywords,
            flow_steps=f.flow_steps,
            use_ai=f.use_ai,
            total_triggers=f.total_triggers,
            total_converted=f.total_converted,
            total_leads=f.total_leads,
            created_at=f.created_at
        )
        for f in funnels
    ]


@router.get("/funnels/{funnel_id}", response_model=FunnelResponse)
async def get_funnel(
    funnel_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get funnel by ID"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(AutoFunnel).where(
            AutoFunnel.id == uuid.UUID(funnel_id),
            AutoFunnel.user_id == uuid.UUID(user_id)
        )
    )
    funnel = result.scalar_one_or_none()
    
    if not funnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funnel not found")
    
    return FunnelResponse(
        id=str(funnel.id),
        name=funnel.name,
        is_active=funnel.is_active,
        trigger_keywords=funnel.trigger_keywords,
        flow_steps=funnel.flow_steps,
        use_ai=funnel.use_ai,
        total_triggers=funnel.total_triggers,
        total_converted=funnel.total_converted,
        total_leads=funnel.total_leads,
        created_at=funnel.created_at
    )


@router.put("/funnels/{funnel_id}", response_model=FunnelResponse)
async def update_funnel(
    funnel_id: str,
    request: FunnelUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update funnel"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(AutoFunnel).where(
            AutoFunnel.id == uuid.UUID(funnel_id),
            AutoFunnel.user_id == uuid.UUID(user_id)
        )
    )
    funnel = result.scalar_one_or_none()
    
    if not funnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funnel not found")
    
    if request.name is not None:
        funnel.name = request.name
    if request.is_active is not None:
        funnel.is_active = request.is_active
    if request.trigger_keywords is not None:
        funnel.trigger_keywords = request.trigger_keywords
    if request.flow_steps is not None:
        funnel.flow_steps = request.flow_steps
    if request.use_ai is not None:
        funnel.use_ai = request.use_ai
    if request.custom_prompt is not None:
        funnel.custom_prompt = request.custom_prompt
    if request.fallback_message is not None:
        funnel.fallback_message = request.fallback_message
    
    await db.commit()
    await db.refresh(funnel)
    
    return FunnelResponse(
        id=str(funnel.id),
        name=funnel.name,
        is_active=funnel.is_active,
        trigger_keywords=funnel.trigger_keywords,
        flow_steps=funnel.flow_steps,
        use_ai=funnel.use_ai,
        total_triggers=funnel.total_triggers,
        total_converted=funnel.total_converted,
        total_leads=funnel.total_leads,
        created_at=funnel.created_at
    )


@router.delete("/funnels/{funnel_id}")
async def delete_funnel(
    funnel_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete funnel"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(AutoFunnel).where(
            AutoFunnel.id == uuid.UUID(funnel_id),
            AutoFunnel.user_id == uuid.UUID(user_id)
        )
    )
    funnel = result.scalar_one_or_none()
    
    if not funnel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funnel not found")
    
    await db.delete(funnel)
    await db.commit()
    
    return {"message": "Funnel deleted successfully"}


# ============================================
# Leads endpoints
# ============================================

@router.get("/leads", response_model=List[LeadListResponse])
async def list_leads(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all leads"""
    
    user_id = current_user.get("user_id")
    
    query = select(Lead).where(Lead.user_id == uuid.UUID(user_id))
    
    if status_filter:
        query = query.where(Lead.status == status_filter)
    
    query = query.order_by(Lead.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    leads = result.scalars().all()
    
    return [
        LeadListResponse(
            id=str(l.id),
            name=l.name,
            contact=l.contact,
            status=l.status,
            source=l.source,
            created_at=l.created_at
        )
        for l in leads
    ]


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get lead details"""
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(Lead).where(
            Lead.id == uuid.UUID(lead_id),
            Lead.user_id == uuid.UUID(user_id)
        )
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    return LeadResponse(
        id=str(lead.id),
        source=lead.source,
        name=lead.name,
        contact=lead.contact,
        status=lead.status,
        conversation=lead.conversation or [],
        booked_at=lead.booked_at,
        created_at=lead.created_at
    )


@router.post("/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: str,
    status: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update lead status"""
    
    user_id = current_user.get("user_id")
    
    valid_statuses = ["new", "contacted", "consultation_booked", "client", "lost"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    result = await db.execute(
        select(Lead).where(
            Lead.id == uuid.UUID(lead_id),
            Lead.user_id == uuid.UUID(user_id)
        )
    )
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    
    lead.status = status
    
    # Update user stats if status changed to client
    if status == "client":
        user_result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = user_result.scalar_one()
        user.total_clients += 1
    
    await db.commit()
    
    return {"message": f"Lead status updated to {status}"}


# ============================================
# Webhook for VK messages
# ============================================

@router.post("/webhook/vk")
async def vk_webhook(
    request: WebhookMessage,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle VK Callback API messages
    """
    
    # Only process message events
    if request.type != "message_new":
        return {"ok": True}
    
    message_obj = request.object
    user_id = message_obj.get("message", {}).get("from_id")
    message_text = message_obj.get("message", {}).get("text", "").lower()
    peer_id = message_obj.get("message", {}).get("peer_id")
    
    if not user_id or not message_text:
        return {"ok": True}
    
    # Find which user (expert) this message belongs to
    # We need to map VK group to user
    # Simplified: find user by vk_group_id
    group_id = str(request.group_id)
    
    # Find user with this VK group
    user_result = await db.execute(
        select(User).where(User.vk_group_id == group_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"No user found for VK group {group_id}")
        return {"ok": True}
    
    # Find active funnel for this user
    funnel_result = await db.execute(
        select(AutoFunnel).where(
            AutoFunnel.user_id == user.id,
            AutoFunnel.is_active == True
        )
    )
    funnel = funnel_result.scalar_one_or_none()
    
    if not funnel:
        # No active funnel, ignore
        return {"ok": True}
    
    # Check if message should trigger funnel
    should_trigger = False
    for keyword in funnel.trigger_keywords:
        if keyword.lower() in message_text:
            should_trigger = True
            break
    
    if not should_trigger:
        # Optional: use AI to determine intent
        if funnel.use_ai:
            background_tasks.add_task(
                process_with_ai,
                user_id=user_id,
                message_text=message_text,
                peer_id=peer_id,
                funnel_id=str(funnel.id),
                user_id_expert=str(user.id)
            )
        return {"ok": True}
    
    # Find or create lead
    lead_result = await db.execute(
        select(Lead).where(
            Lead.vk_user_id == str(user_id),
            Lead.user_id == user.id,
            Lead.status.in_(["new", "contacted"])
        )
    )
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        lead = Lead(
            tenant_id=user.tenant_id,
            user_id=user.id,
            source="vk_direct",
            funnel_id=funnel.id,
            vk_user_id=str(user_id),
            status="new",
            conversation=[]
        )
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        
        # Update funnel stats
        funnel.total_triggers += 1
        funnel.total_leads += 1
        await db.commit()
    
    # Add message to conversation
    conversation = lead.conversation or []
    conversation.append({
        "role": "user",
        "content": message_text,
        "timestamp": datetime.utcnow().isoformat()
    })
    lead.conversation = conversation
    await db.commit()
    
    # Generate response based on flow
    background_tasks.add_task(
        process_funnel_step,
        lead_id=str(lead.id),
        funnel_id=str(funnel.id),
        current_step=1,
        message_text=message_text,
        peer_id=peer_id
    )
    
    return {"ok": True}


async def process_funnel_step(
    lead_id: str,
    funnel_id: str,
    current_step: int,
    message_text: str,
    peer_id: int
):
    """Process funnel step and send response"""
    
    async with get_db_context() as db:
        # Get funnel
        result = await db.execute(
            select(AutoFunnel).where(AutoFunnel.id == uuid.UUID(funnel_id))
        )
        funnel = result.scalar_one()
        
        # Get lead
        lead_result = await db.execute(
            select(Lead).where(Lead.id == uuid.UUID(lead_id))
        )
        lead = lead_result.scalar_one()
        
        # Get steps
        steps = funnel.flow_steps
        
        # Find step
        step = None
        for s in steps:
            if s.get("step") == current_step:
                step = s
                break
        
        if not step:
            # Use fallback
            response_text = funnel.fallback_message or "Спасибо за сообщение. Эксперт свяжется с вами в ближайшее время."
        else:
            step_type = step.get("type")
            step_content = step.get("content")
            
            if step_type == "message":
                response_text = step_content
            elif step_type == "ask_contact":
                response_text = step_content
            elif step_type == "send_material":
                response_text = step_content
            elif step_type == "ask_booking":
                response_text = step_content
            else:
                response_text = step_content or "Спасибо! Я передам ваш вопрос эксперту."
            
            # Replace placeholders
            response_text = response_text.replace("[name]", lead.name or "гость")
        
        # Send response via VK API
        vk_service = VKService()
        await vk_service.send_message(peer_id, response_text)
        
        # Add response to conversation
        conversation = lead.conversation or []
        conversation.append({
            "role": "assistant",
            "content": response_text,
            "step": current_step,
            "timestamp": datetime.utcnow().isoformat()
        })
        lead.conversation = conversation
        await db.commit()
        
        # Schedule next step if needed
        delay_minutes = step.get("delay_minutes", 0)
        if delay_minutes > 0 and current_step < len(steps):
            # Schedule next step
            pass  # Implement with Celery


async def process_with_ai(
    vk_user_id: str,
    message_text: str,
    peer_id: int,
    funnel_id: str,
    user_id_expert: str
):
    """Process message with AI to generate response"""
    
    ai_service = AIService()
    
    # Generate response
    result = await ai_service.generate_reply(
        message=message_text,
        specialization="nutrition"  # Get from user context
    )
    
    response_text = result.get("reply", "Спасибо за вопрос! Я передам его эксперту.")
    
    # Send response via VK API
    vk_service = VKService()
    await vk_service.send_message(peer_id, response_text)
