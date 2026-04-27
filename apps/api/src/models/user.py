"""
User model (SQLAlchemy)
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, 
    Text, JSON, DECIMAL, ForeignKey, Table
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Auth
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255))
    avatar_url = Column(Text)
    phone = Column(String(50))
    
    # VK integration
    vk_group_id = Column(String(100))
    vk_access_token = Column(Text)
    vk_group_name = Column(String(255))
    
    # Telegram integration
    telegram_bot_token = Column(Text)
    telegram_chat_id = Column(String(100))
    
    # Subscription
    current_tier = Column(String(50), default="start")  # start, pro, expert
    subscription_status = Column(String(50), default="trial")  # trial, active, expired, cancelled
    subscription_expires_at = Column(DateTime)
    
    # Settings
    voice_style = Column(Text)
    uniqueness = Column(Text)
    forbidden_topics = Column(ARRAY(String))
    
    # Stats
    total_leads = Column(Integer, default=0)
    total_clients = Column(Integer, default=0)
    total_revenue = Column(DECIMAL(10, 2), default=0)
    
    # Timestamps
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.email}>"
