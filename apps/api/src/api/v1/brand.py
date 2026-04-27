"""
Personal Brand API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.tenant import get_current_tenant
from src.models.user import User
from src.services.ai_service import AIService
from src.services.vk_service import VKService

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic schemas
class PositioningRequest(BaseModel):
    """Request for positioning generation"""
    specialization: str = Field(..., description="Специализация: nutrition, psychology, tarot, fitness")
    experience_years: int = Field(..., description="Лет опыта")
    clients_count: int = Field(..., description="Количество клиентов")
    main_result: str = Field(..., description="Главный результат, который получают клиенты")
    superpower: str = Field(..., description="Ваша суперсила (что уникального вы даёте)")
    target_audience: str = Field(..., description="Целевая аудитория")
    values: List[str] = Field(default=[], description="Ценности")
    tone: str = Field(default="Эксперт, но без пафоса", description="Тон общения")


class PositioningResponse(BaseModel):
    """Positioning generation result"""
    one_liner: str  # Короткая фраза для шапки профиля
    elevator_pitch: str  # 30-секундная презентация
    description: str  # Развёрнутое описание для страницы
    taglines: List[str]  # 5-10 вариантов слоганов
    positioning_map: Dict[str, str]  # Чем отличается от других


class StoryRequest(BaseModel):
    """Request for personal story generation"""
    background: str = Field(..., description="Предыстория: откуда пришли, что было до")
    turning_point: str = Field(..., description="Точка перелома: что заставило меняться")
    learning: str = Field(..., description="Чему научились на своём опыте")
    results: str = Field(..., description="Каких результатов достигли сами и с клиентами")
    mission: str = Field(..., description="Миссия: зачем вы это делаете")
    audience_connection: str = Field(..., description="Что общего с аудиторией")


class StoryResponse(BaseModel):
    """Personal story generation result"""
    story: str  # Полная история для страницы «Об авторе»
    short_version: str  # Короткая версия для закреплённого поста
    video_script: str  # Сценарий видео/рилс
    key_phrases: List[str]  # Ключевые фразы, которые можно повторять


class TrustAuditRequest(BaseModel):
    """Request for trust audit"""
    vk_page_url: str = Field(..., description="Ссылка на страницу ВК")


class TrustAuditResponse(BaseModel):
    """Trust audit result"""
    overall_score: int  # 0-100
    scores: Dict[str, int]  # По категориям
    issues: List[str]
    recommendations: List[str]
    quick_wins: List[Dict[str, str]]  # Что можно сделать за 5 минут


class UniquenessRequest(BaseModel):
    """Request for uniqueness analysis"""
    vk_page_url: str = Field(..., description="Ссылка на страницу ВК")
    competitors_urls: List[str] = Field(default=[], description="Ссылки на страницы конкурентов")


class UniquenessResponse(BaseModel):
    """Uniqueness analysis result"""
    your_positioning: str  # Как вы позиционируетесь сейчас
    zone_of_uniqueness: str  # Зона уникальности
    common_pitfalls: List[str]  # Что делают все (и вам не стоит)
    differentiators: List[str]  # Чем вы отличаетесь
    recommended_focus: str  # На чём фокусироваться


class VoiceStyleResponse(BaseModel):
    """Voice style analysis result"""
    current_voice: Dict[str, Any]  # Как вы звучите сейчас
    suggested_voice: Dict[str, Any]  # Как лучше звучать
    phrases_to_use: List[str]  # Фразы, которые стоит использовать
    phrases_to_avoid: List[str]  # Фразы, которых стоит избегать


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
# Positioning endpoints
# ============================================

@router.post("/positioning", response_model=PositioningResponse)
async def generate_positioning(
    request: PositioningRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate positioning (УТП) for expert
    Available on Expert plan
    """
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "brand_story"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brand positioning is available on Expert plan only. Please upgrade."
        )
    
    user_id = current_user.get("user_id")
    
    # Get user for personalization
    user_result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = user_result.scalar_one_or_none()
    
    # Generate positioning via AI
    ai_service = AIService()
    result = await ai_service.generate_positioning(
        specialization=request.specialization,
        experience_years=request.experience_years,
        clients_count=request.clients_count,
        main_result=request.main_result,
        superpower=request.superpower,
        target_audience=request.target_audience,
        values=request.values,
        tone=request.tone
    )
    
    # Save to user profile (optional)
    if user and result.get("one_liner"):
        user.uniqueness = result.get("one_liner")
        await db.commit()
    
    return PositioningResponse(
        one_liner=result.get("one_liner", ""),
        elevator_pitch=result.get("elevator_pitch", ""),
        description=result.get("description", ""),
        taglines=result.get("taglines", []),
        positioning_map=result.get("positioning_map", {})
    )


@router.post("/positioning/from-vk")
async def generate_positioning_from_vk(
    vk_page_url: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate positioning based on existing VK page analysis
    """
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "brand_story"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brand positioning is available on Expert plan only."
        )
    
    # Parse VK page
    vk_service = VKService()
    group_id = vk_service.extract_group_id(vk_page_url)
    
    if not group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid VK page URL"
        )
    
    # Get group info and posts
    group_info = await vk_service.get_group_info(group_id)
    posts = await vk_service.get_wall_posts(group_id, count=20)
    
    # Analyze current positioning
    ai_service = AIService()
    result = await ai_service.analyze_current_positioning(
        group_info=group_info,
        posts=posts
    )
    
    return result


# ============================================
# Personal story endpoints
# ============================================

@router.post("/story", response_model=StoryResponse)
async def generate_personal_story(
    request: StoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate personal story for "About" page and videos
    Available on Expert plan
    """
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "brand_story"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Personal story generation is available on Expert plan only."
        )
    
    ai_service = AIService()
    result = await ai_service.generate_personal_story(
        background=request.background,
        turning_point=request.turning_point,
        learning=request.learning,
        results=request.results,
        mission=request.mission,
        audience_connection=request.audience_connection
    )
    
    return StoryResponse(
        story=result.get("story", ""),
        short_version=result.get("short_version", ""),
        video_script=result.get("video_script", ""),
        key_phrases=result.get("key_phrases", [])
    )


# ============================================
# Trust audit endpoints
# ============================================

@router.post("/trust-audit", response_model=TrustAuditResponse)
async def trust_audit(
    request: TrustAuditRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Audit VK page for trust signals
    Available on Expert plan
    """
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "trust_audit"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trust audit is available on Expert plan only. Please upgrade."
        )
    
    # Parse VK page
    vk_service = VKService()
    group_id = vk_service.extract_group_id(request.vk_page_url)
    
    if not group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid VK page URL"
        )
    
    # Get data
    group_info = await vk_service.get_group_info(group_id)
    posts = await vk_service.get_wall_posts(group_id, count=20)
    pinned_post = await vk_service.get_pinned_post(group_id)
    comments = await vk_service.get_post_comments(group_id, posts[0].get("id", 0)) if posts else []
    
    # Analyze trust signals
    ai_service = AIService()
    result = await ai_service.analyze_trust_signals(
        group_info=group_info,
        posts=posts,
        pinned_post=pinned_post,
        comments=comments
    )
    
    return TrustAuditResponse(
        overall_score=result.get("overall_score", 0),
        scores=result.get("scores", {}),
        issues=result.get("issues", []),
        recommendations=result.get("recommendations", []),
        quick_wins=result.get("quick_wins", [])
    )


@router.get("/trust-audit/checklist")
async def get_trust_checklist(
    current_user: dict = Depends(get_current_user)
):
    """
    Get checklist for trust signals (without auditing specific page)
    """
    
    return {
        "checklist": [
            {"category": "Профиль", "items": [
                {"name": "Аватар с лицом", "weight": 10},
                {"name": "Обложка с УТП", "weight": 5},
                {"name": "Заполненное описание", "weight": 10},
                {"name": "Контактные данные", "weight": 10}
            ]},
            {"category": "Контент", "items": [
                {"name": "Кейсы клиентов (3+)", "weight": 15},
                {"name": "Отзывы (5+)", "weight": 10},
                {"name": "Фото/видео с лицами", "weight": 5},
                {"name": "Образовательные посты", "weight": 5}
            ]},
            {"category": "Вовлечение", "items": [
                {"name": "Ответы на комментарии", "weight": 10},
                {"name": "Активность в комментариях", "weight": 5},
                {"name": "Прямые эфиры", "weight": 5}
            ]},
            {"category": "Криденшиалы", "items": [
                {"name": "Дипломы/сертификаты", "weight": 5},
                {"name": "Человек-ссылка: фото с наставниками", "weight": 5},
                {"name": "Публикации в СМИ", "weight": 5}
            ]}
        ],
        "total_max_score": 100,
        "your_score": None  # Will be filled after audit
    }


# ============================================
# Uniqueness analysis endpoints
# ============================================

@router.post("/uniqueness", response_model=UniquenessResponse)
async def analyze_uniqueness(
    request: UniquenessRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze what makes you unique compared to competitors
    Available on Expert plan
    """
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "uniqueness_analysis"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Uniqueness analysis is available on Expert plan only."
        )
    
    vk_service = VKService()
    ai_service = AIService()
    
    # Get your page data
    your_group_id = vk_service.extract_group_id(request.vk_page_url)
    if not your_group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid VK page URL"
        )
    
    your_info = await vk_service.get_group_info(your_group_id)
    your_posts = await vk_service.get_wall_posts(your_group_id, count=20)
    
    # Get competitors data
    competitors_data = []
    for comp_url in request.competitors_urls[:5]:  # Max 5 competitors
        comp_id = vk_service.extract_group_id(comp_url)
        if comp_id:
            comp_info = await vk_service.get_group_info(comp_id)
            comp_posts = await vk_service.get_wall_posts(comp_id, count=15)
            competitors_data.append({
                "name": comp_info.get("name") if comp_info else comp_url,
                "description": comp_info.get("description") if comp_info else "",
                "posts": comp_posts
            })
    
    # Analyze uniqueness
    result = await ai_service.analyze_uniqueness(
        your_info=your_info,
        your_posts=your_posts,
        competitors=competitors_data
    )
    
    return UniquenessResponse(
        your_positioning=result.get("your_positioning", ""),
        zone_of_uniqueness=result.get("zone_of_uniqueness", ""),
        common_pitfalls=result.get("common_pitfalls", []),
        differentiators=result.get("differentiators", []),
        recommended_focus=result.get("recommended_focus", "")
    )


# ============================================
# Voice style endpoints
# ============================================

@router.post("/voice/analyze")
async def analyze_voice_style(
    sample_texts: List[str],
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze current voice style from sample texts
    """
    
    ai_service = AIService()
    result = await ai_service.analyze_voice_style(sample_texts)
    
    return VoiceStyleResponse(
        current_voice=result.get("current", {}),
        suggested_voice=result.get("suggested", {}),
        phrases_to_use=result.get("phrases_to_use", []),
        phrases_to_avoid=result.get("phrases_to_avoid", [])
    )


@router.post("/voice/save")
async def save_voice_style(
    voice_style: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save voice style to user profile
    """
    
    user_id = current_user.get("user_id")
    
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.voice_style = voice_style
    await db.commit()
    
    return {"message": "Voice style saved successfully"}


# ============================================
# Landing page builder
# ============================================

class LandingPageRequest(BaseModel):
    """Request for landing page generation"""
    service_name: str = Field(..., description="Название услуги")
    price: float = Field(..., description="Цена")
    target_audience: str = Field(..., description="Целевая аудитория")
    main_problem: str = Field(..., description="Главная проблема клиента")
    solution: str = Field(..., description="Как вы решаете проблему")
    results: List[str] = Field(..., description="Результаты, которые получают клиенты")
    objections: List[str] = Field(default=[], description="Главные возражения")
    special_offer: Optional[str] = Field(None, description="Спецпредложение")
    deadline: Optional[str] = Field(None, description="Дедлайн (если есть)")


class LandingPageResponse(BaseModel):
    """Generated landing page"""
    title: str
    subtitle: str
    sections: List[Dict[str, Any]]
    cta_button_text: str
    full_html: str
    preview_text: str


@router.post("/landing-page", response_model=LandingPageResponse)
async def generate_landing_page(
    request: LandingPageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate landing page copy for service
    Available on Expert plan
    """
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "landing_builder"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Landing page builder is available on Expert plan only."
        )
    
    ai_service = AIService()
    result = await ai_service.generate_landing_page(
        service_name=request.service_name,
        price=request.price,
        target_audience=request.target_audience,
        main_problem=request.main_problem,
        solution=request.solution,
        results=request.results,
        objections=request.objections,
        special_offer=request.special_offer,
        deadline=request.deadline
    )
    
    return LandingPageResponse(
        title=result.get("title", ""),
        subtitle=result.get("subtitle", ""),
        sections=result.get("sections", []),
        cta_button_text=result.get("cta_button_text", "Записаться"),
        full_html=result.get("full_html", ""),
        preview_text=result.get("preview_text", "")
    )
