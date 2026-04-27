"""
VK Audit models (SQLAlchemy)
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.models.user import Base


class VKAudit(Base):
    __tablename__ = "vk_audits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Input
    vk_page_url = Column(String(500), nullable=False)
    vk_group_id = Column(String(100), nullable=False)
    
    # Results
    result = Column(JSON, nullable=False)
    score = Column(Integer)  # 0-100
    recommendations = Column(JSON)
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<VKAudit {self.vk_group_id}>"


class VKAuditDetail(Base):
    __tablename__ = "vk_audit_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("vk_audits.id", ondelete="CASCADE"), nullable=False)
    
    category = Column(String(100), nullable=False)  # cover, avatar, pinned, content, comments, etc
    score = Column(Integer)
    max_score = Column(Integer)
    issues = Column(JSON)
    recommendations = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<VKAuditDetail {self.category}>"
