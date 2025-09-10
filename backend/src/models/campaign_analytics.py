"""
CampaignAnalytics model for traffic simulation platform.
Represents campaign-level aggregated metrics.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Integer, Numeric, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class CampaignAnalytics(Base):
    """CampaignAnalytics model representing campaign-level aggregated metrics."""
    
    __tablename__ = 'campaign_analytics'
    
    # Primary key
    id: UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign key
    campaign_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Completion metrics
    total_sessions: int = Column(Integer, nullable=False)
    completed_sessions: int = Column(Integer, nullable=False)
    failed_sessions: int = Column(Integer, nullable=False)
    success_rate: Decimal = Column(Numeric(3, 2), nullable=False)
    
    # Performance metrics
    avg_session_duration_ms: Optional[Decimal] = Column(Numeric(12, 2), nullable=True)
    avg_pages_per_session: Optional[Decimal] = Column(Numeric(4, 2), nullable=True)
    avg_actions_per_session: Optional[Decimal] = Column(Numeric(6, 2), nullable=True)
    
    # Quality metrics
    avg_rhythm_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    behavioral_variance: Optional[Decimal] = Column(Numeric(6, 3), nullable=True)
    detection_risk_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    
    # Resource usage
    total_runtime_ms: Optional[int] = Column(BigInteger, nullable=True)
    avg_cpu_usage: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    peak_memory_mb: Optional[int] = Column(Integer, nullable=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_analytics")
    
    def __repr__(self) -> str:
        return f"<CampaignAnalytics(id={self.id}, campaign_id={self.campaign_id}, success_rate={self.success_rate})>"
    
    def to_dict(self) -> dict:
        """Convert campaign analytics to dictionary."""
        return {
            'id': str(self.id),
            'campaign_id': str(self.campaign_id),
            'total_sessions': self.total_sessions,
            'completed_sessions': self.completed_sessions,
            'failed_sessions': self.failed_sessions,
            'success_rate': float(self.success_rate),
            'avg_session_duration_ms': float(self.avg_session_duration_ms) if self.avg_session_duration_ms else None,
            'avg_pages_per_session': float(self.avg_pages_per_session) if self.avg_pages_per_session else None,
            'avg_actions_per_session': float(self.avg_actions_per_session) if self.avg_actions_per_session else None,
            'avg_rhythm_score': float(self.avg_rhythm_score) if self.avg_rhythm_score else None,
            'behavioral_variance': float(self.behavioral_variance) if self.behavioral_variance else None,
            'detection_risk_score': float(self.detection_risk_score) if self.detection_risk_score else None,
            'total_runtime_ms': self.total_runtime_ms,
            'avg_cpu_usage': float(self.avg_cpu_usage) if self.avg_cpu_usage else None,
            'peak_memory_mb': self.peak_memory_mb,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CampaignAnalytics':
        """Create campaign analytics from dictionary."""
        return cls(
            campaign_id=UUID(data['campaign_id']),
            total_sessions=data['total_sessions'],
            completed_sessions=data['completed_sessions'],
            failed_sessions=data['failed_sessions'],
            success_rate=Decimal(str(data['success_rate'])),
            avg_session_duration_ms=Decimal(str(data['avg_session_duration_ms'])) if data.get('avg_session_duration_ms') else None,
            avg_pages_per_session=Decimal(str(data['avg_pages_per_session'])) if data.get('avg_pages_per_session') else None,
            avg_actions_per_session=Decimal(str(data['avg_actions_per_session'])) if data.get('avg_actions_per_session') else None,
            avg_rhythm_score=Decimal(str(data['avg_rhythm_score'])) if data.get('avg_rhythm_score') else None,
            behavioral_variance=Decimal(str(data['behavioral_variance'])) if data.get('behavioral_variance') else None,
            detection_risk_score=Decimal(str(data['detection_risk_score'])) if data.get('detection_risk_score') else None,
            total_runtime_ms=data.get('total_runtime_ms'),
            avg_cpu_usage=Decimal(str(data['avg_cpu_usage'])) if data.get('avg_cpu_usage') else None,
            peak_memory_mb=data.get('peak_memory_mb')
        )
    
    def calculate_success_rate(self) -> Decimal:
        """Calculate success rate from completed and failed sessions."""
        if self.total_sessions == 0:
            return Decimal('0.0')
        
        return Decimal(str(self.completed_sessions)) / Decimal(str(self.total_sessions))
    
    def calculate_avg_session_duration(self, session_durations: list) -> Optional[Decimal]:
        """Calculate average session duration from list of durations."""
        if not session_durations:
            return None
        
        total_duration = sum(session_durations)
        return Decimal(str(total_duration)) / Decimal(str(len(session_durations)))
    
    def calculate_avg_pages_per_session(self, page_counts: list) -> Optional[Decimal]:
        """Calculate average pages per session from list of page counts."""
        if not page_counts:
            return None
        
        total_pages = sum(page_counts)
        return Decimal(str(total_pages)) / Decimal(str(len(page_counts)))
    
    def calculate_avg_actions_per_session(self, action_counts: list) -> Optional[Decimal]:
        """Calculate average actions per session from list of action counts."""
        if not action_counts:
            return None
        
        total_actions = sum(action_counts)
        return Decimal(str(total_actions)) / Decimal(str(len(action_counts)))
    
    def calculate_avg_rhythm_score(self, rhythm_scores: list) -> Optional[Decimal]:
        """Calculate average rhythm score from list of rhythm scores."""
        if not rhythm_scores:
            return None
        
        valid_scores = [score for score in rhythm_scores if score is not None]
        if not valid_scores:
            return None
        
        total_score = sum(valid_scores)
        return Decimal(str(total_score)) / Decimal(str(len(valid_scores)))
    
    def calculate_behavioral_variance(self, rhythm_scores: list) -> Optional[Decimal]:
        """Calculate behavioral variance from rhythm scores."""
        if len(rhythm_scores) < 2:
            return None
        
        valid_scores = [float(score) for score in rhythm_scores if score is not None]
        if len(valid_scores) < 2:
            return None
        
        mean_score = sum(valid_scores) / len(valid_scores)
        variance = sum((score - mean_score) ** 2 for score in valid_scores) / len(valid_scores)
        
        return Decimal(str(variance))
    
    def calculate_detection_risk_score(self, rhythm_scores: list, action_variances: list) -> Optional[Decimal]:
        """Calculate detection risk score based on rhythm and variance patterns."""
        if not rhythm_scores and not action_variances:
            return None
        
        # Combine rhythm scores and action variances for risk assessment
        all_scores = []
        if rhythm_scores:
            all_scores.extend([float(score) for score in rhythm_scores if score is not None])
        if action_variances:
            all_scores.extend([float(var) for var in action_variances if var is not None])
        
        if not all_scores:
            return None
        
        # Calculate risk based on how "robotic" the patterns are
        # Lower rhythm scores and lower variance = more robotic = higher risk
        avg_score = sum(all_scores) / len(all_scores)
        
        # Invert the score so lower human-like behavior = higher detection risk
        risk_score = max(0.0, min(1.0, 1.0 - avg_score))
        
        return Decimal(str(risk_score))
    
    def update_timestamps(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
