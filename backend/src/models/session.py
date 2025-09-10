"""
Session model for traffic simulation platform.
Represents individual simulation sessions.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class SessionStatus(str, Enum):
    """Session status enumeration."""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    TIMEOUT = 'timeout'


class Session(Base):
    """Session model representing individual simulation sessions."""
    
    __tablename__ = 'sessions'
    
    # Primary key
    id: UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign keys
    campaign_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    persona_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('personas.id'), nullable=False)
    
    # Status and timing
    status: str = Column(String(20), nullable=False, server_default='pending')
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    completed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    
    # Session configuration
    start_url: str = Column(String(500), nullable=False)
    user_agent: str = Column(Text, nullable=False)
    viewport_width: int = Column(Integer, nullable=False, server_default='1920')
    viewport_height: int = Column(Integer, nullable=False, server_default='1080')
    
    # Session metrics
    session_duration_ms: Optional[int] = Column(Integer, nullable=True)
    pages_visited: int = Column(Integer, nullable=False, server_default='0')
    total_actions: int = Column(Integer, nullable=False, server_default='0')
    error_message: Optional[str] = Column(Text, nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="sessions")
    persona = relationship("Persona", back_populates="sessions")
    page_visits = relationship("PageVisit", back_populates="session", cascade="all, delete-orphan")
    session_analytics = relationship("SessionAnalytics", back_populates="session", uselist=False)
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, campaign_id={self.campaign_id}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            'id': str(self.id),
            'campaign_id': str(self.campaign_id),
            'persona_id': str(self.persona_id),
            'status': self.status,
            'start_url': self.start_url,
            'user_agent': self.user_agent,
            'viewport_width': self.viewport_width,
            'viewport_height': self.viewport_height,
            'session_duration_ms': self.session_duration_ms,
            'pages_visited': self.pages_visited,
            'total_actions': self.total_actions,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """Create session from dictionary."""
        return cls(
            campaign_id=UUID(data['campaign_id']),
            persona_id=UUID(data['persona_id']),
            start_url=data['start_url'],
            user_agent=data['user_agent'],
            viewport_width=data.get('viewport_width', 1920),
            viewport_height=data.get('viewport_height', 1080)
        )
    
    def can_start(self) -> bool:
        """Check if session can be started."""
        return self.status == SessionStatus.PENDING
    
    def can_complete(self) -> bool:
        """Check if session can be completed."""
        return self.status == SessionStatus.RUNNING
    
    def can_fail(self) -> bool:
        """Check if session can be marked as failed."""
        return self.status in [SessionStatus.PENDING, SessionStatus.RUNNING]
    
    def start(self) -> None:
        """Start the session."""
        if not self.can_start():
            raise ValueError(f"Cannot start session in status: {self.status}")
        
        self.status = SessionStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self, duration_ms: Optional[int] = None) -> None:
        """Complete the session."""
        if not self.can_complete():
            raise ValueError(f"Cannot complete session in status: {self.status}")
        
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if duration_ms is not None:
            self.session_duration_ms = duration_ms
    
    def fail(self, error_message: Optional[str] = None) -> None:
        """Mark session as failed."""
        if not self.can_fail():
            raise ValueError(f"Cannot fail session in status: {self.status}")
        
        self.status = SessionStatus.FAILED
        self.completed_at = datetime.utcnow()
        if error_message:
            self.error_message = error_message
    
    def timeout(self) -> None:
        """Mark session as timed out."""
        if not self.can_fail():
            raise ValueError(f"Cannot timeout session in status: {self.status}")
        
        self.status = SessionStatus.TIMEOUT
        self.completed_at = datetime.utcnow()
    
    def calculate_duration_ms(self) -> Optional[int]:
        """Calculate session duration in milliseconds."""
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            return int(duration.total_seconds() * 1000)
        return None
