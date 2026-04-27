"""
Marathon models (SQLAlchemy)
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid

from src.models.user import Base


class Marathon(Base):
    __tablename__ = "marathons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    cover_image_url = Column(Text)
    
    # Structure
    duration_days = Column(Integer, nullable=False)
    goals = Column(JSON, default=[])  # ["цель1", "цель2"]
    
    # Content
    structure = Column(JSON, default=[])  # days, topics, tasks, bonuses
    generated_content = Column(JSON, default={})  # all posts, tasks, emails
    
    # Settings
    platform = Column(String(50), default="telegram")  # telegram, vk, whatsapp
    is_free = Column(Boolean, default=True)
    price = Column(DECIMAL(10, 2))
    
    # Communication
    welcome_message = Column(Text)
    completion_message = Column(Text)
    reminder_hours = Column(ARRAY(Integer), default=[1, 24])  # hours before
    
    # Stats
    participants_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    dropped_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)  # converted to paid
    conversion_revenue = Column(DECIMAL(10, 2), default=0)
    
    # Offer after marathon
    upsell_message = Column(Text)
    upsell_link = Column(Text)
    
    # Status
    status = Column(String(50), default="draft")  # draft, active, completed, archived
    
    # Scheduling
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<Marathon {self.name}>"


class MarathonParticipant(Base):
    __tablename__ = "marathon_participants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marathon_id = Column(UUID(as_uuid=True), ForeignKey("marathons.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # null if not registered user
    
    # Participant info
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    contact = Column(String(255))  # telegram username or vk id
    source = Column(String(255))  # how they found
    
    # Progress
    current_day = Column(Integer, default=1)
    completed_days = Column(ARRAY(Integer), default=[])
    homework_submissions = Column(JSON, default=[])
    homework_scores = Column(JSON, default=[])
    
    # Engagement
    last_active_at = Column(DateTime)
    messages_sent = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="active")  # active, completed, dropped
    
    # Conversion
    converted_to_client = Column(Boolean, default=False)
    converted_value = Column(DECIMAL(10, 2))
    converted_at = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<MarathonParticipant {self.name}>"


class MarathonDay(Base):
    """Individual day content for marathon"""
    __tablename__ = "marathon_days"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marathon_id = Column(UUID(as_uuid=True), ForeignKey("marathons.id", ondelete="CASCADE"), nullable=False)
    
    day_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Content
    text = Column(Text)  # Main content
    video_url = Column(Text)
    audio_url = Column(Text)
    
    # Task
    task_title = Column(String(255))
    task_description = Column(Text)
    task_type = Column(String(50), default="text")  # text, photo, file, quiz
    
    # Bonus material
    bonus_title = Column(String(255))
    bonus_file_url = Column(Text)
    
    # Schedule
    scheduled_for = Column(Integer)  # days from start (0 = day 1 at start)
    send_time = Column(String(5), default="10:00")  # HH:MM
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<MarathonDay {self.day_number}: {self.title}>"
