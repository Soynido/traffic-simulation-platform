"""
SessionAnalytics model for traffic simulation platform.
Represents aggregated session metrics for faster reporting.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class SessionAnalytics(Base):
    """SessionAnalytics model representing aggregated session metrics."""
    
    __tablename__ = 'session_analytics'
    
    # Primary key
    id: UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign keys
    session_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, unique=True)
    campaign_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    persona_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('personas.id'), nullable=False)
    
    # Timing metrics
    total_duration_ms: int = Column(Integer, nullable=False)
    avg_page_dwell_time_ms: Optional[Decimal] = Column(Numeric(10, 2), nullable=True)
    median_page_dwell_time_ms: Optional[int] = Column(Integer, nullable=True)
    
    # Navigation metrics
    pages_visited: int = Column(Integer, nullable=False)
    navigation_depth: int = Column(Integer, nullable=False)
    bounce_rate: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    
    # Interaction metrics
    total_actions: int = Column(Integer, nullable=False)
    actions_per_page: Optional[Decimal] = Column(Numeric(4, 2), nullable=True)
    click_through_rate: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    scroll_engagement: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    
    # Behavioral patterns
    action_variance: Optional[Decimal] = Column(Numeric(6, 3), nullable=True)
    rhythm_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    pause_distribution: Optional[Dict[str, Any]] = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="session_analytics")
    campaign = relationship("Campaign")
    persona = relationship("Persona", back_populates="session_analytics")
    
    def __repr__(self) -> str:
        return f"<SessionAnalytics(id={self.id}, session_id={self.session_id}, pages_visited={self.pages_visited})>"
    
    def to_dict(self) -> dict:
        """Convert session analytics to dictionary."""
        return {
            'id': str(self.id),
            'session_id': str(self.session_id),
            'campaign_id': str(self.campaign_id),
            'persona_id': str(self.persona_id),
            'total_duration_ms': self.total_duration_ms,
            'avg_page_dwell_time_ms': float(self.avg_page_dwell_time_ms) if self.avg_page_dwell_time_ms else None,
            'median_page_dwell_time_ms': self.median_page_dwell_time_ms,
            'pages_visited': self.pages_visited,
            'navigation_depth': self.navigation_depth,
            'bounce_rate': float(self.bounce_rate) if self.bounce_rate else None,
            'total_actions': self.total_actions,
            'actions_per_page': float(self.actions_per_page) if self.actions_per_page else None,
            'click_through_rate': float(self.click_through_rate) if self.click_through_rate else None,
            'scroll_engagement': float(self.scroll_engagement) if self.scroll_engagement else None,
            'action_variance': float(self.action_variance) if self.action_variance else None,
            'rhythm_score': float(self.rhythm_score) if self.rhythm_score else None,
            'pause_distribution': self.pause_distribution,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SessionAnalytics':
        """Create session analytics from dictionary."""
        return cls(
            session_id=UUID(data['session_id']),
            campaign_id=UUID(data['campaign_id']),
            persona_id=UUID(data['persona_id']),
            total_duration_ms=data['total_duration_ms'],
            avg_page_dwell_time_ms=Decimal(str(data['avg_page_dwell_time_ms'])) if data.get('avg_page_dwell_time_ms') else None,
            median_page_dwell_time_ms=data.get('median_page_dwell_time_ms'),
            pages_visited=data['pages_visited'],
            navigation_depth=data['navigation_depth'],
            bounce_rate=Decimal(str(data['bounce_rate'])) if data.get('bounce_rate') else None,
            total_actions=data['total_actions'],
            actions_per_page=Decimal(str(data['actions_per_page'])) if data.get('actions_per_page') else None,
            click_through_rate=Decimal(str(data['click_through_rate'])) if data.get('click_through_rate') else None,
            scroll_engagement=Decimal(str(data['scroll_engagement'])) if data.get('scroll_engagement') else None,
            action_variance=Decimal(str(data['action_variance'])) if data.get('action_variance') else None,
            rhythm_score=Decimal(str(data['rhythm_score'])) if data.get('rhythm_score') else None,
            pause_distribution=data.get('pause_distribution')
        )
    
    def calculate_bounce_rate(self) -> Decimal:
        """Calculate bounce rate (1 if only 1 page, 0 if more than 1 page)."""
        if self.pages_visited <= 1:
            return Decimal('1.0')
        return Decimal('0.0')
    
    def calculate_actions_per_page(self) -> Optional[Decimal]:
        """Calculate average actions per page."""
        if self.pages_visited > 0:
            return Decimal(str(self.total_actions)) / Decimal(str(self.pages_visited))
        return None
    
    def calculate_scroll_engagement(self, page_visits: list) -> Optional[Decimal]:
        """Calculate average scroll engagement from page visits."""
        if not page_visits:
            return None
        
        total_scroll = sum(visit.get('scroll_depth_percent', 0) for visit in page_visits)
        return Decimal(str(total_scroll)) / Decimal(str(len(page_visits))) / Decimal('100')
    
    def calculate_rhythm_score(self, action_timestamps: list) -> Optional[Decimal]:
        """Calculate rhythm score based on action timing patterns."""
        if len(action_timestamps) < 3:
            return None
        
        # Calculate intervals between actions
        intervals = []
        for i in range(1, len(action_timestamps)):
            interval = (action_timestamps[i] - action_timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return None
        
        # Calculate coefficient of variation (lower = more rhythmic)
        mean_interval = sum(intervals) / len(intervals)
        if mean_interval == 0:
            return Decimal('0.0')
        
        variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5
        cv = std_dev / mean_interval
        
        # Convert to 0-1 scale where 1 is most human-like (less rhythmic)
        rhythm_score = min(1.0, max(0.0, cv))
        return Decimal(str(rhythm_score))
