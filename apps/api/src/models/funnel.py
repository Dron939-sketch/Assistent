"""
Auto funnel and leads models (SQLAlchemy)
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.models.user import Base


class AutoFunnel(Base):
    __tablename__ = "auto_funnels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Trigger rules
    trigger_keywords = Column(JSON, default=[])  # ["дорого", "сколько стоит", "цены"]
    trigger_on_contains = Column(Boolean, default=True)
    trigger_on_exact = Column(Boolean, default=False)
    
    # Response flow
    flow_steps = Column(JSON, default=[
        {"step": 1, "type": "message", "content": "", "delay_minutes": 0},
        {"step": 2, "type": "ask_contact", "content": "Оставьте телефон, я пришлю подробности", "delay_minutes": 0},
        {"step": 3, "type": "send_material", "content": "Вот полезный гайд", "delay_minutes": 0},
        {"step": 4, "type": "ask_booking", "content": "Записаться на консультацию?", "delay_minutes": 0}
    ])
    
    # Advanced settings
    custom_prompt = Column(Text)
    use_ai = Column(Boolean, default=True)
    max_conversation_turns = Column(Integer, default=10)
    fallback_message = Column(Text, default="Этот вопрос требует личного ответа. Я передам его эксперту.")
    
    # Stats
    total_triggers = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    total_leads = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<AutoFunnel {self.name}>"


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Source
    source = Column(String(100), nullable=False)  # vk_direct, vk_comment, telegram, marathon, landing
    funnel_id = Column(UUID(as_uuid=True), ForeignKey("auto_funnels.id"))
    
    # Contact
    contact = Column(String(255))  # phone, tg, email
    name = Column(String(255))
    vk_user_id = Column(String(100))
    tg_user_id = Column(String(100))
    
    # Conversation history
    conversation = Column(JSON, default=[])  # full chat history
    
    # Status
    status = Column(String(50), default="new")  # new, contacted, consultation_booked, client, lost
    
    # Consultation
    booked_at = Column(DateTime)
    consultation_link = Column(Text)
    
    # Value
    estimated_value = Column(DECIMAL(10, 2))
    actual_value = Column(DECIMAL(10, 2))
    
    # Notes
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<Lead {self.id}>"


class FunnelSession(Base):
    """Track active funnel sessions for users"""
    __tablename__ = "funnel_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    funnel_id = Column(UUID(as_uuid=True), ForeignKey("auto_funnels.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    
    current_step = Column(Integer, default=1)
    last_message_at = Column(DateTime, server_default=func.now())
    context = Column(JSON, default={})
    
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
