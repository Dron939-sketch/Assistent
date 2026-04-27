"""
Tenant model (SQLAlchemy)
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.models.user import Base


class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False)
    domain = Column(String(255))
    
    # Configuration
    config = Column(JSON, default={})
    branding = Column(JSON, default={})
    ai_config = Column(JSON, default={})
    
    # Status
    status = Column(String(50), default="active")
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Tenant {self.tenant_id}>"
