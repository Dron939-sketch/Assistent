"""
Content generation models (SQLAlchemy)
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.models.user import Base


class ContentGeneration(Base):
    __tablename__ = "content_generations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Type: post, reply, marathon_day, story, case, checklist, landing_text
    type = Column(String(50), nullable=False)
    topic = Column(String(500))
    
    # Input
    input_text = Column(Text)
    input_voice_url = Column(Text)  # S3 URL for voice input
    input_voice_transcript = Column(Text)  # Transcribed text
    
    # Output
    output_text = Column(Text)
    output_metadata = Column(JSON)  # Additional data: title, hashtags, suggested_images, etc
    
    # For posts: generation history (versions)
    versions = Column(JSON, default=[])  # Store previous versions for user to choose
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Usage
    tokens_used = Column(Integer)
    cost = Column(Integer)  # in cents or smallest unit
    
    # Publishing
    published_at = Column(DateTime)
    vk_post_id = Column(String(100))
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ContentGeneration {self.type}:{self.id}>"


class ContentCalendar(Base):
    __tablename__ = "content_calendar"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(500), nullable=False)
    content = Column(Text)
    content_type = Column(String(50))  # post, story, video, article
    theme = Column(String(255))
    hashtags = Column(JSON, default=[])
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=False)
    timezone = Column(String(50), default="Europe/Moscow")
    published_at = Column(DateTime)
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, published, failed, cancelled
    
    # VK
    vk_post_id = Column(String(100))
    vk_post_url = Column(Text)
    
    # Generation reference
    generation_id = Column(UUID(as_uuid=True), ForeignKey("content_generations.id"))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<ContentCalendar {self.title}>"
