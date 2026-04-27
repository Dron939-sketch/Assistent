"""
Analytics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
import uuid
import logging

from src.core.database import get_db
from src.core.security import get_current_user
from src.core.tenant import get_current_tenant
from src.models.analytics import DailyAnalytics, LeveragePoint, UserForecast
from src.models.funnel import Lead
from src.models.user import User
from src.services.ai_service import AIService

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic schemas
class DashboardMetrics(BaseModel):
    """Main dashboard metrics"""
    # Current period (last 30 days)
    period_start: datetime
    period_end: datetime
    
    # Leads
    total_leads: int
    leads_change_percent: float
    
    # Clients
    total_clients: int
    clients_change_percent: float
    
    # Revenue
    total_revenue: float
    revenue_change_percent: float
    
    # Conversion rates
    lead_to_consultation_rate: float  # leads that booked consultation
    consultation_to_client_rate: float  # consultations that became clients
    overall_conversion_rate: float  # leads to clients
    
    # Engagement
    avg_engagement_rate: float
    total_subscribers: int
    subscribers_growth: float
    
    # Currently active
    active_leads: int  # leads in progress
    active_marathons: int
    scheduled_posts: int


class LeadsChartData(BaseModel):
    """Leads over time"""
    labels: List[str]  # dates
    leads: List[int]
    consultations: List[int]
    clients: List[int]


class EngagementChartData(BaseModel):
    """Engagement over time"""
    labels: List[str]  # dates
    reach: List[int]
    likes: List[int]
    comments: List[int]
    er: List[float]


class LeveragePointResponse(BaseModel):
    """Leverage point suggestion"""
    id: str
    action: str
    effort_hours: float
    expected_impact: str
    completed: bool
    date: date


class LeveragePointComplete(BaseModel):
    """Mark leverage point as completed"""
    actual_impact: str
    actual_leads_increase: Optional[int] = None


class ForecastResponse(BaseModel):
    """Monthly forecast"""
    month: date
    forecasted_leads: int
    forecasted_clients: int
    forecasted_revenue: float
    actual_leads: Optional[int]
    actual_clients: Optional[int]
    actual_revenue: Optional[float]
    confidence_score: int


class ROIReport(BaseModel):
    """ROI report"""
    total_spent: float  # on subscription + ads (if tracked)
    total_earned: float
    roi_percent: float
    payback_days: int  # days to recover investment
    customer_ltv: float  # lifetime value
    customer_cac: float  # customer acquisition cost


class CompetitorAnalysis(BaseModel):
    """Competitor analysis result"""
    competitor_name: str
    metrics: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    your_advantage: str


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
# Dashboard endpoints
# ============================================

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = 30
):
    """Get main dashboard metrics"""
    
    user_id = current_user.get("user_id")
    user_uuid = uuid.UUID(user_id)
    
    # Date ranges
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    previous_start = start_date - timedelta(days=days)
    
    # Get leads stats
    leads_result = await db.execute(
        select(
            func.count(Lead.id).filter(Lead.created_at >= start_date).label("current_leads"),
            func.count(Lead.id).filter(
                and_(
                    Lead.created_at >= previous_start,
                    Lead.created_at < start_date
                )
            ).label("previous_leads"),
            func.count(Lead.id).filter(
                and_(
                    Lead.status == "consultation_booked",
                    Lead.created_at >= start_date
                )
            ).label("consultations"),
            func.count(Lead.id).filter(
                and_(
                    Lead.status == "client",
                    Lead.created_at >= start_date
                )
            ).label("clients")
        ).where(Lead.user_id == user_uuid)
    )
    leads_stats = leads_result.one()
    
    current_leads = leads_stats.current_leads or 0
    previous_leads = leads_stats.previous_leads or 0
    consultations = leads_stats.consultations or 0
    clients = leads_stats.clients or 0
    
    leads_change = ((current_leads - previous_leads) / previous_leads * 100) if previous_leads > 0 else 0
    
    # Get revenue
    revenue_result = await db.execute(
        select(
            func.sum(DailyAnalytics.revenue).filter(DailyAnalytics.day >= start_date.date()).label("current_revenue"),
            func.sum(DailyAnalytics.revenue).filter(
                and_(
                    DailyAnalytics.day >= previous_start.date(),
                    DailyAnalytics.day < start_date.date()
                )
            ).label("previous_revenue")
        ).where(DailyAnalytics.user_id == user_uuid)
    )
    revenue_stats = revenue_result.one()
    
    current_revenue = float(revenue_stats.current_revenue or 0)
    previous_revenue = float(revenue_stats.previous_revenue or 0)
    revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    
    # Get user for subscriber count
    user_result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = user_result.scalar_one_or_none()
    
    # Get active marathons count
    from src.models.marathon import Marathon
    marathon_result = await db.execute(
        select(func.count(Marathon.id)).where(
            Marathon.user_id == user_uuid,
            Marathon.status == "active"
        )
    )
    active_marathons = marathon_result.scalar() or 0
    
    # Get scheduled posts count
    from src.models.content import ContentCalendar
    scheduled_result = await db.execute(
        select(func.count(ContentCalendar.id)).where(
            ContentCalendar.user_id == user_uuid,
            ContentCalendar.status == "scheduled",
            ContentCalendar.scheduled_for >= datetime.utcnow()
        )
    )
    scheduled_posts = scheduled_result.scalar() or 0
    
    # Calculate conversion rates
    lead_to_consultation = (consultations / current_leads * 100) if current_leads > 0 else 0
    consultation_to_client = (clients / consultations * 100) if consultations > 0 else 0
    overall_conversion = (clients / current_leads * 100) if current_leads > 0 else 0
    
    # Get engagement data for last 30 days
    engagement_result = await db.execute(
        select(
            func.avg(DailyAnalytics.er),
            func.sum(DailyAnalytics.new_subscribers),
            func.sum(DailyAnalytics.lost_subscribers)
        ).where(
            DailyAnalytics.user_id == user_uuid,
            DailyAnalytics.day >= start_date.date()
        )
    )
    engagement_stats = engagement_result.one()
    
    avg_er = float(engagement_stats.avg or 0)
    new_subs = engagement_stats.sum or 0
    lost_subs = engagement_stats.lost_subscribers or 0
    net_growth = new_subs - lost_subs
    total_subs = user.total_subscribers if user else 0
    
    return DashboardMetrics(
        period_start=start_date,
        period_end=end_date,
        total_leads=current_leads,
        leads_change_percent=round(leads_change, 1),
        total_clients=clients,
        clients_change_percent=0,  # Would need more data
        total_revenue=current_revenue,
        revenue_change_percent=round(revenue_change, 1),
        lead_to_consultation_rate=round(lead_to_consultation, 1),
        consultation_to_client_rate=round(consultation_to_client, 1),
        overall_conversion_rate=round(overall_conversion, 1),
        avg_engagement_rate=round(avg_er, 1),
        total_subscribers=total_subs,
        subscribers_growth=round(net_growth, 1),
        active_leads=0,  # Would need query for leads in progress (new or contacted)
        active_marathons=active_marathons,
        scheduled_posts=scheduled_posts
    )


@router.get("/leads-chart", response_model=LeadsChartData)
async def get_leads_chart(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = 30
):
    """Get leads data for chart"""
    
    user_id = current_user.get("user_id")
    user_uuid = uuid.UUID(user_id)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query leads by day
    result = await db.execute(
        select(
            func.date(Lead.created_at).label("day"),
            func.count(Lead.id).label("leads"),
            func.count(Lead.id).filter(Lead.status == "consultation_booked").label("consultations"),
            func.count(Lead.id).filter(Lead.status == "client").label("clients")
        )
        .where(
            Lead.user_id == user_uuid,
            Lead.created_at >= start_date
        )
        .group_by(func.date(Lead.created_at))
        .order_by(func.date(Lead.created_at))
    )
    
    rows = result.all()
    
    # Fill all days
    labels = []
    leads_data = []
    consultations_data = []
    clients_data = []
    
    current = start_date.date()
    today = datetime.utcnow().date()
    
    row_dict = {row.day: row for row in rows}
    
    while current <= today:
        labels.append(current.strftime("%d.%m"))
        row = row_dict.get(current)
        leads_data.append(row.leads if row else 0)
        consultations_data.append(row.consultations if row else 0)
        clients_data.append(row.clients if row else 0)
        current += timedelta(days=1)
    
    return LeadsChartData(
        labels=labels,
        leads=leads_data,
        consultations=consultations_data,
        clients=clients_data
    )


@router.get("/engagement-chart", response_model=EngagementChartData)
async def get_engagement_chart(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = 30
):
    """Get engagement data for chart"""
    
    user_id = current_user.get("user_id")
    user_uuid = uuid.UUID(user_id)
    
    start_date_obj = datetime.utcnow().date() - timedelta(days=days)
    
    result = await db.execute(
        select(DailyAnalytics)
        .where(
            DailyAnalytics.user_id == user_uuid,
            DailyAnalytics.day >= start_date_obj
        )
        .order_by(DailyAnalytics.day)
    )
    rows = result.all()
    
    labels = []
    reach = []
    likes = []
    comments = []
    er = []
    
    for row in rows:
        labels.append(row.day.strftime("%d.%m"))
        reach.append(row.posts_reach or 0)
        likes.append(row.posts_likes or 0)
        comments.append(row.posts_comments or 0)
        er.append(float(row.er or 0))
    
    return EngagementChartData(
        labels=labels,
        reach=reach,
        likes=likes,
        comments=comments,
        er=er
    )


# ============================================
# Leverage points (рычаги)
# ============================================

@router.get("/leverage", response_model=List[LeveragePointResponse])
async def get_leverage_points(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 5
):
    """Get current leverage point suggestions"""
    
    user_tier = current_user.get("tier", "start")
    if not check_tier_access(user_tier, "leverage_point"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Leverage points are available on Pro and Expert plans."
        )
    
    user_id = current_user.get("user_id")
    user_uuid = uuid.UUID(user_id)
    
    # Get unresolved leverage points
    result = await db.execute(
        select(LeveragePoint)
        .where(
            LeveragePoint.user_id == user_uuid,
            LeveragePoint.completed == 0
        )
        .order_by(LeveragePoint.date.desc())
        .limit(limit)
    )
    points = result.scalars().all()
    
    if not points:
        # Generate new leverage points
        points = await generate_leverage_points(user_uuid, db)
    
    return [
        LeveragePointResponse(
            id=str(p.id),
            action=p.action,
            effort_hours=float(p.effort_hours) if p.effort_hours else 0,
            expected_impact=p.expected_impact or "",
            completed=bool(p.completed),
            date=p.date
        )
        for p in points
    ]


@router.post("/leverage/{point_id}/complete")
async def complete_leverage_point(
    point_id: str,
    request: LeveragePointComplete,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark leverage point as completed"""
    
    user_id = current_user.get("user_id")
    user_uuid = uuid.UUID(user_id)
    
    result = await db.execute(
        select(LeveragePoint).where(
            LeveragePoint.id == uuid.UUID(point_id),
            LeveragePoint.user_id == user_uuid
        )
    )
    point = result.scalar_one_or_none()
    
    if not point:
        raise HTTPException(status_code=404, detail="Leverage point not found")
    
    point.completed = 1
    point.completed_at = datetime.utcnow()
    point.actual_impact = request.actual_impact
    point.actual_leads_increase = request.actual_leads_increase
    
    await db.commit()
    
    return {"message": "Leverage point marked as completed"}


async def generate_leverage_points(user_uuid: uuid.UUID, db: AsyncSession) -> List[LeveragePoint]:
    """Generate leverage point suggestions using AI"""
    
    # Get user data
    user_result = await db.execute(
        select(User).where(User.id == user_uuid)
    )
    user = user_result.scalar_one_or_none()
    
    # Get recent analytics
    analytics_result = await db.execute(
        select(DailyAnalytics)
        .where(DailyAnalytics.user_id == user_uuid)
        .order_by(DailyAnalytics.day.desc())
        .limit(30)
    )
    analytics = analytics_result.scalars().all()
    
    # Get recent leads
    leads_result = await db.execute(
        select(Lead)
        .where(Lead.user_id == user_uuid)
        .order_by(Lead.created_at.desc())
        .limit(20)
    )
    leads = leads_result.scalars().all()
    
    # Format data for AI
    context = {
        "current_tier": user.current_tier if user else "start",
        "total_leads": user.total_leads if user else 0,
        "total_clients": user.total_clients if user else 0,
        "avg_leads_per_day": sum(a.new_leads for a in analytics) / len(analytics) if analytics else 0,
        "avg_engagement_rate": sum(a.er for a in analytics) / len(analytics) if analytics else 0,
        "recent_objections": get_common_objections(leads)
    }
    
    # Generate suggestions via AI
    ai_service = AIService()
    suggestions = await ai_service.generate_leverage_suggestions(context)
    
    # Save to database
    leverage_points = []
    for suggestion in suggestions[:5]:
        point = LeveragePoint(
            user_id=user_uuid,
            tenant_id=user.tenant_id if user else None,
            date=datetime.utcnow().date(),
            action=suggestion["action"],
            effort_hours=suggestion.get("effort_hours", 0),
            expected_impact=suggestion.get("expected_impact", ""),
            completed=0
        )
        db.add(point)
        leverage_points.append(point)
    
    await db.commit()
    
    return leverage_points


def get_common_objections(leads: List[Lead]) -> List[str]:
    """Extract common objections from leads conversations"""
    objections = []
    objection_keywords = ["дорого", "подумаю", "нет времени", "сложно", "не получится", "не верю"]
    
    for lead in leads:
        if lead.conversation:
            for msg in lead.conversation:
                text = msg.get("content", "").lower()
                for kw in objection_keywords:
                    if kw in text:
                        objections.append(kw)
                        break
    
    from collections import Counter
    return [obj for obj, _ in Counter(objections).most_common(3)]


# ============================================
# Forecast endpoints
# ============================================

@router.get("/forecast", response_model=List[ForecastResponse])
async def get_forecast(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    months: int = 3
):
    """Get monthly forecasts"""
    
    user_id = current_user.get("user_id")
    user_uuid = uuid.UUID(user_id)
    
    # Get forecasts
    result = await db.execute(
        select(UserForecast)
        .where(UserForecast.user_id == user_uuid)
        .order_by(UserForecast.month)
        .limit(months)
    )
    forecasts = result.scalars().all()
    
    # Generate forecasts if missing
    if not forecasts:
        forecasts = await generate_forecast(user_uuid, db, months)
    
    return [
        ForecastResponse(
            month=f.month,
            forecasted_leads=f.forecasted_leads or 0,
            forecasted_clients=f.forecasted_clients or 0,
            forecasted_revenue=float(f.forecasted_revenue or 0),
            actual_leads=f.actual_leads,
            actual_clients=f.actual_clients,
            actual_revenue=float(f.actual_revenue) if f.actual_revenue else None,
            confidence_score=f.confidence_score or 70
        )
        for f in forecasts
    ]


async def generate_forecast(user_uuid: uuid.UUID, db: AsyncSession, months: int) -> List[UserForecast]:
    """Generate forecast for upcoming months"""
    
    # Get historical data
    analytics_result = await db.execute(
        select(DailyAnalytics)
        .where(DailyAnalytics.user_id == user_uuid)
        .order_by(DailyAnalytics.day.desc())
        .limit(90)
    )
    analytics = analytics_result.scalars().all()
    
    # Calculate trends
    avg_monthly_leads = sum(a.new_leads for a in analytics) / max(3, len(analytics) / 30) if analytics else 0
    avg_conversion_rate = sum(a.leads_client for a in analytics) / max(1, sum(a.new_leads for a in analytics)) if analytics else 0
    avg_revenue_per_client = await get_avg_revenue_per_client(user_uuid, db)
    
    forecasts = []
    today = datetime.utcnow().date()
    
    for i in range(1, months + 1):
        month_date = date(today.year, today.month, 1)
        if i > 1:
            month_date = month_date.replace(month=month_date.month + i - 1)
        
        forecasted_leads = int(avg_monthly_leads * (1 + i * 0.05))  # 5% growth assumption
        forecasted_clients = int(forecasted_leads * avg_conversion_rate)
        forecasted_revenue = forecasted_clients * avg_revenue_per_client
        
        forecast = UserForecast(
            user_id=user_uuid,
            tenant_id=None,
            month=month_date,
            forecasted_leads=forecasted_leads,
            forecasted_clients=forecasted_clients,
            forecasted_revenue=forecasted_revenue,
            confidence_score=90 if i == 1 else 70 if i == 2 else 50
        )
        db.add(forecast)
        forecasts.append(forecast)
    
    await db.commit()
    return forecasts


async def get_avg_revenue_per_client(user_uuid: uuid.UUID, db: AsyncSession) -> float:
    """Calculate average revenue per client"""
    
    from src.models.marathon import MarathonParticipant
    
    result = await db.execute(
        select(func.avg(Lead.actual_value))
        .where(Lead.user_id == user_uuid, Lead.status == "client")
    )
    avg = result.scalar()
    
    return float(avg) if avg else 5000  # default


# ============================================
# ROI and competitor analytics
# ============================================

@router.get("/roi", response_model=ROIReport)
async def get_roi_report(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ROI report for the service"""
    
    user_id = current_user.get("user_id")
    user_uuid = uuid.UUID(user_id)
    
    subscription_cost = get_subscription_cost(current_user.get("tier", "start"))
    
    # Get total revenue from analytics
    revenue_result = await db.execute(
        select(func.sum(DailyAnalytics.revenue))
        .where(DailyAnalytics.user_id == user_uuid)
    )
    total_revenue = float(revenue_result.scalar() or 0)
    
    # Get client count
    client_result = await db.execute(
        select(func.count(Lead.id))
        .where(
            Lead.user_id == user_uuid,
            Lead.status == "client"
        )
    )
    total_clients = client_result.scalar() or 1
    
    customer_ltv = total_revenue / total_clients if total_clients > 0 else 0
    customer_cac = subscription_cost * 3  # assume 3 months to acquire a client
    
    roi_percent = ((total_revenue - subscription_cost * 12) / (subscription_cost * 12) * 100) if subscription_cost > 0 else 0
    
    return ROIReport(
        total_spent=subscription_cost * 12,
        total_earned=total_revenue,
        roi_percent=round(roi_percent, 1),
        payback_days=30,  # simplified
        customer_ltv=round(customer_ltv, 0),
        customer_cac=round(customer_cac, 0)
    )


def get_subscription_cost(tier: str) -> float:
    """Get monthly subscription cost for tier"""
    costs = {
        "start": 1490,
        "pro": 3490,
        "expert": 7990
    }
    return costs.get(tier, 1490)


@router.get("/competitors")
async def analyze_competitors(
    competitor_urls: List[str] = Query(..., description="URLs of competitor VK pages"),
    current_user: dict = Depends(get_current_user)
):
    """Analyze competitors and find your advantages"""
    
    user_tier = current_user.get("tier", "start")
    if user_tier != "expert":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Competitor analysis is available on Expert plan only."
        )
    
    vk_service = VKService()
    competitors_data = []
    
    for url in competitor_urls[:5]:
        group_id = vk_service.extract_group_id(url)
        if group_id:
            info = await vk_service.get_group_info(group_id)
            posts = await vk_service.get_wall_posts(group_id, count=15)
            competitors_data.append({
                "name": info.get("name") if info else url,
                "subscribers": info.get("members_count", 0) if info else 0,
                "posts_count": len(posts),
                "avg_likes": sum(p.get("likes", {}).get("count", 0) for p in posts) / max(1, len(posts))
            })
    
    # Analyze with AI
    ai_service = AIService()
    result = await ai_service.analyze_competitors(competitors_data)
    
    return result
