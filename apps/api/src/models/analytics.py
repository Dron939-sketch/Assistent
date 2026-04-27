"""
Analytics models (SQLAlchemy)
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, DECIMAL, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.models.user import Base


class DailyAnalytics(Base):
    """Daily aggregated analytics for user"""
    __tablename__ = "daily_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    day = Column(Date, nullable=False)
    
    # Growth metrics
    new_subscribers = Column(Integer, default=0)
    total_subscribers = Column(Integer, default=0)
    lost_subscribers = Column(Integer, default=0)
    
    # Engagement metrics
    posts_count = Column(Integer, default=0)
    posts_reach = Column(Integer, default=0)
    posts_likes = Column(Integer, default=0)
    posts_comments = Column(Integer, default=0)
    posts_shares = Column(Integer, default=0)
    er = Column(DECIMAL(5, 2))  # engagement rate
    
    # Leads metrics
    new_leads = Column(Integer, default=0)
    leads_consultation = Column(Integer, default=0)  # booked consultation
    leads_client = Column(Integer, default=0)  # became client
    leads_lost = Column(Integer, default=0)
    
    # Revenue
    revenue = Column(DECIMAL(10, 2), default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DailyAnalytics {self.day}>"


class LeveragePoint(Base):
    """Leverage point suggestions (рычаги)"""
    __tablename__ = "leverage_points"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    date = Column(Date, nullable=False)
    
    # Suggestion
    action = Column(String(500), nullable=False)
    effort_hours = Column(DECIMAL(5, 2))
    expected_impact = Column(String(255))
    
    # Whether user completed
    completed = Column(Integer, default=0)  # 0=not completed, 1=completed
    completed_at = Column(DateTime)
    
    # Actual result
    actual_impact = Column(Text)
    actual_leads_increase = Column(Integer)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<LeveragePoint {self.date}: {self.action[:50]}>"


class UserForecast(Base):
    """Monthly forecast for user"""
    __tablename__ = "user_forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    month = Column(Date, nullable=False)  # first day of month
    
    # Forecasted values
    forecasted_leads = Column(Integer)
    forecasted_clients = Column(Integer)
    forecasted_revenue = Column(DECIMAL(10, 2))
    
    # Actual values (after month ends)
    actual_leads = Column(Integer)
    actual_clients = Column(Integer)
    actual_revenue = Column(DECIMAL(10, 2))
    
    # Confidence
    confidence_score = Column(Integer, default=70)  # 0-100
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<UserForecast {self.month}>"
