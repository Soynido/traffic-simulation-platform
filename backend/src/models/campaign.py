"""
Campaign model for traffic simulation platform.
Represents simulation campaign configuration.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    PENDING = 'pending'
    RUNNING = 'running'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'


class Campaign(Base):
    """Campaign model representing simulation campaign configuration."""
    
    __tablename__ = 'campaigns'
    
    # Primary key
    id: UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Basic information
    name: str = Column(String(200), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    target_url: str = Column(String(500), nullable=False)
    
    # Session configuration
    total_sessions: int = Column(Integer, nullable=False)
    concurrent_sessions: int = Column(Integer, nullable=False, server_default='10')
    
    # Status and timing
    status: str = Column(String(20), nullable=False, server_default='pending')
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    completed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    persona_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('personas.id'), nullable=False)
    
    # Configuration
    rate_limit_delay_ms: int = Column(Integer, nullable=False, server_default='1000')
    user_agent_rotation: bool = Column(Boolean, nullable=False, server_default='true')
    respect_robots_txt: bool = Column(Boolean, nullable=False, server_default='true')
    
    # Relationships
    persona = relationship("Persona", back_populates="campaigns")
    sessions = relationship("Session", back_populates="campaign", cascade="all, delete-orphan")
    campaign_analytics = relationship("CampaignAnalytics", back_populates="campaign", uselist=False)
    
    # Check constraints
    __table_args__ = (
        CheckConstraint('total_sessions > 0', name='ck_campaigns_total_sessions_positive'),
        CheckConstraint('concurrent_sessions > 0', name='ck_campaigns_concurrent_sessions_positive'),
        CheckConstraint('concurrent_sessions <= total_sessions', name='ck_campaigns_concurrent_sessions_lte_total'),
        CheckConstraint('rate_limit_delay_ms >= 100', name='ck_campaigns_rate_limit_delay_minimum'),
        CheckConstraint("status IN ('pending', 'running', 'paused', 'completed', 'failed')", name='ck_campaigns_status_valid'),
    )
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert campaign to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'target_url': self.target_url,
            'total_sessions': self.total_sessions,
            'concurrent_sessions': self.concurrent_sessions,
            'status': self.status,
            'persona_id': str(self.persona_id),
            'rate_limit_delay_ms': self.rate_limit_delay_ms,
            'user_agent_rotation': self.user_agent_rotation,
            'respect_robots_txt': self.respect_robots_txt,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Campaign':
        """Create campaign from dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description'),
            target_url=data['target_url'],
            total_sessions=data['total_sessions'],
            concurrent_sessions=data.get('concurrent_sessions', 10),
            persona_id=UUID(data['persona_id']),
            rate_limit_delay_ms=data.get('rate_limit_delay_ms', 1000),
            user_agent_rotation=data.get('user_agent_rotation', True),
            respect_robots_txt=data.get('respect_robots_txt', True)
        )
    
    def can_start(self) -> bool:
        """Check if campaign can be started."""
        return self.status == CampaignStatus.PENDING
    
    def can_pause(self) -> bool:
        """Check if campaign can be paused."""
        return self.status == CampaignStatus.RUNNING
    
    def can_resume(self) -> bool:
        """Check if campaign can be resumed."""
        return self.status == CampaignStatus.PAUSED
    
    def start(self) -> None:
        """Start the campaign."""
        if not self.can_start():
            raise ValueError(f"Cannot start campaign in status: {self.status}")
        
        self.status = CampaignStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def pause(self) -> None:
        """Pause the campaign."""
        if not self.can_pause():
            raise ValueError(f"Cannot pause campaign in status: {self.status}")
        
        self.status = CampaignStatus.PAUSED
        self.updated_at = datetime.utcnow()
    
    def resume(self) -> None:
        """Resume the campaign."""
        if not self.can_resume():
            raise ValueError(f"Cannot resume campaign in status: {self.status}")
        
        self.status = CampaignStatus.RUNNING
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark campaign as completed."""
        self.status = CampaignStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def fail(self) -> None:
        """Mark campaign as failed."""
        self.status = CampaignStatus.FAILED
        self.updated_at = datetime.utcnow()
