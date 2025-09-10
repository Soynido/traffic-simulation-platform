"""
PageVisit model for traffic simulation platform.
Represents individual page visits within sessions.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class PageVisit(Base):
    """PageVisit model representing individual page visits within sessions."""
    
    __tablename__ = 'page_visits'
    
    # Primary key
    id: UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign key
    session_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    
    # Page information
    url: str = Column(String(500), nullable=False)
    title: Optional[str] = Column(Text, nullable=True)
    visit_order: int = Column(Integer, nullable=False)
    
    # Timing
    arrived_at: datetime = Column(DateTime(timezone=True), nullable=False)
    left_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    
    # Metrics
    actions_count: int = Column(Integer, nullable=False, server_default='0')
    scroll_depth_percent: int = Column(Integer, nullable=False, server_default='0')
    
    # Relationships
    session = relationship("Session", back_populates="page_visits")
    actions = relationship("Action", back_populates="page_visit", cascade="all, delete-orphan")
    
    # Check constraints
    __table_args__ = (
        CheckConstraint('visit_order > 0', name='ck_page_visits_visit_order_positive'),
        CheckConstraint('scroll_depth_percent BETWEEN 0 AND 100', name='ck_page_visits_scroll_depth_range'),
    )
    
    def __repr__(self) -> str:
        return f"<PageVisit(id={self.id}, session_id={self.session_id}, url='{self.url}', order={self.visit_order})>"
    
    def to_dict(self) -> dict:
        """Convert page visit to dictionary."""
        return {
            'id': str(self.id),
            'session_id': str(self.session_id),
            'url': self.url,
            'title': self.title,
            'visit_order': self.visit_order,
            'arrived_at': self.arrived_at.isoformat() if self.arrived_at else None,
            'left_at': self.left_at.isoformat() if self.left_at else None,
            'dwell_time_ms': self.dwell_time_ms,
            'actions_count': self.actions_count,
            'scroll_depth_percent': self.scroll_depth_percent
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PageVisit':
        """Create page visit from dictionary."""
        return cls(
            session_id=UUID(data['session_id']),
            url=data['url'],
            title=data.get('title'),
            visit_order=data['visit_order'],
            arrived_at=datetime.fromisoformat(data['arrived_at'].replace('Z', '+00:00')) if data.get('arrived_at') else datetime.utcnow(),
            left_at=datetime.fromisoformat(data['left_at'].replace('Z', '+00:00')) if data.get('left_at') else None,
            actions_count=data.get('actions_count', 0),
            scroll_depth_percent=data.get('scroll_depth_percent', 0)
        )
    
    @property
    def dwell_time_ms(self) -> Optional[int]:
        """Calculate dwell time in milliseconds."""
        if self.arrived_at and self.left_at:
            duration = self.left_at - self.arrived_at
            return int(duration.total_seconds() * 1000)
        return None
    
    def leave(self) -> None:
        """Mark the page visit as left."""
        if not self.left_at:
            self.left_at = datetime.utcnow()
    
    def add_action(self) -> None:
        """Increment action count."""
        self.actions_count += 1
    
    def update_scroll_depth(self, depth_percent: int) -> None:
        """Update scroll depth percentage."""
        if 0 <= depth_percent <= 100:
            self.scroll_depth_percent = depth_percent
        else:
            raise ValueError("Scroll depth must be between 0 and 100")
