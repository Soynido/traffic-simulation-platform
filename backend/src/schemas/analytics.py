"""
Pydantic schemas for analytics API.
Defines request/response models for analytics endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field


class SessionAnalyticsResponse(BaseModel):
    """Schema for session analytics response."""
    id: UUID = Field(..., description="Analytics ID")
    session_id: UUID = Field(..., description="Session ID")
    campaign_id: UUID = Field(..., description="Campaign ID")
    persona_id: UUID = Field(..., description="Persona ID")
    
    # Timing metrics
    total_duration_ms: int = Field(..., description="Total session duration in milliseconds")
    avg_page_dwell_time_ms: Optional[float] = Field(None, description="Average page dwell time in milliseconds")
    median_page_dwell_time_ms: Optional[int] = Field(None, description="Median page dwell time in milliseconds")
    
    # Navigation metrics
    pages_visited: int = Field(..., description="Number of pages visited")
    navigation_depth: int = Field(..., description="Navigation depth")
    bounce_rate: Optional[float] = Field(None, description="Bounce rate")
    
    # Interaction metrics
    total_actions: int = Field(..., description="Total number of actions")
    actions_per_page: Optional[float] = Field(None, description="Average actions per page")
    click_through_rate: Optional[float] = Field(None, description="Click-through rate")
    scroll_engagement: Optional[float] = Field(None, description="Scroll engagement score")
    
    # Behavioral patterns
    action_variance: Optional[float] = Field(None, description="Action timing variance")
    rhythm_score: Optional[float] = Field(None, description="Rhythm score (human-likeness)")
    pause_distribution: Optional[Dict[str, Any]] = Field(None, description="Pause distribution")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, analytics):
        """Create response from ORM model."""
        return cls(
            id=analytics.id,
            session_id=analytics.session_id,
            campaign_id=analytics.campaign_id,
            persona_id=analytics.persona_id,
            total_duration_ms=analytics.total_duration_ms,
            avg_page_dwell_time_ms=float(analytics.avg_page_dwell_time_ms) if analytics.avg_page_dwell_time_ms else None,
            median_page_dwell_time_ms=analytics.median_page_dwell_time_ms,
            pages_visited=analytics.pages_visited,
            navigation_depth=analytics.navigation_depth,
            bounce_rate=float(analytics.bounce_rate) if analytics.bounce_rate else None,
            total_actions=analytics.total_actions,
            actions_per_page=float(analytics.actions_per_page) if analytics.actions_per_page else None,
            click_through_rate=float(analytics.click_through_rate) if analytics.click_through_rate else None,
            scroll_engagement=float(analytics.scroll_engagement) if analytics.scroll_engagement else None,
            action_variance=float(analytics.action_variance) if analytics.action_variance else None,
            rhythm_score=float(analytics.rhythm_score) if analytics.rhythm_score else None,
            pause_distribution=analytics.pause_distribution,
            created_at=analytics.created_at
        )


class CampaignAnalyticsResponse(BaseModel):
    """Schema for campaign analytics response."""
    id: UUID = Field(..., description="Analytics ID")
    campaign_id: UUID = Field(..., description="Campaign ID")
    
    # Completion metrics
    total_sessions: int = Field(..., description="Total number of sessions")
    completed_sessions: int = Field(..., description="Number of completed sessions")
    failed_sessions: int = Field(..., description="Number of failed sessions")
    success_rate: float = Field(..., description="Success rate")
    
    # Performance metrics
    avg_session_duration_ms: Optional[float] = Field(None, description="Average session duration in milliseconds")
    avg_pages_per_session: Optional[float] = Field(None, description="Average pages per session")
    avg_actions_per_session: Optional[float] = Field(None, description="Average actions per session")
    
    # Quality metrics
    avg_rhythm_score: Optional[float] = Field(None, description="Average rhythm score")
    behavioral_variance: Optional[float] = Field(None, description="Behavioral variance")
    detection_risk_score: Optional[float] = Field(None, description="Detection risk score")
    
    # Resource usage
    total_runtime_ms: Optional[int] = Field(None, description="Total runtime in milliseconds")
    avg_cpu_usage: Optional[float] = Field(None, description="Average CPU usage percentage")
    peak_memory_mb: Optional[int] = Field(None, description="Peak memory usage in MB")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, analytics):
        """Create response from ORM model."""
        return cls(
            id=analytics.id,
            campaign_id=analytics.campaign_id,
            total_sessions=analytics.total_sessions,
            completed_sessions=analytics.completed_sessions,
            failed_sessions=analytics.failed_sessions,
            success_rate=float(analytics.success_rate),
            avg_session_duration_ms=float(analytics.avg_session_duration_ms) if analytics.avg_session_duration_ms else None,
            avg_pages_per_session=float(analytics.avg_pages_per_session) if analytics.avg_pages_per_session else None,
            avg_actions_per_session=float(analytics.avg_actions_per_session) if analytics.avg_actions_per_session else None,
            avg_rhythm_score=float(analytics.avg_rhythm_score) if analytics.avg_rhythm_score else None,
            behavioral_variance=float(analytics.behavioral_variance) if analytics.behavioral_variance else None,
            detection_risk_score=float(analytics.detection_risk_score) if analytics.detection_risk_score else None,
            total_runtime_ms=analytics.total_runtime_ms,
            avg_cpu_usage=float(analytics.avg_cpu_usage) if analytics.avg_cpu_usage else None,
            peak_memory_mb=analytics.peak_memory_mb,
            created_at=analytics.created_at,
            updated_at=analytics.updated_at
        )


class AnalyticsSummaryResponse(BaseModel):
    """Schema for analytics summary response."""
    total_sessions: int = Field(..., description="Total number of sessions")
    completed_sessions: int = Field(..., description="Number of completed sessions")
    failed_sessions: int = Field(..., description="Number of failed sessions")
    success_rate: float = Field(..., description="Success rate")
    avg_session_duration_ms: float = Field(..., description="Average session duration in milliseconds")
    avg_pages_per_session: float = Field(..., description="Average pages per session")
    avg_actions_per_session: float = Field(..., description="Average actions per session")
    avg_rhythm_score: float = Field(..., description="Average rhythm score")
    detection_risk_score: float = Field(..., description="Detection risk score")


class ComparisonCriteria(BaseModel):
    """Schema for comparison criteria."""
    name: str = Field(..., description="Name for this criteria")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    campaign_id: Optional[UUID] = Field(None, description="Campaign ID filter")


class ComparisonRequest(BaseModel):
    """Schema for analytics comparison request."""
    criteria: List[ComparisonCriteria] = Field(..., min_items=2, description="List of criteria to compare")


class ComparisonResponse(BaseModel):
    """Schema for analytics comparison response."""
    criteria: List[ComparisonCriteria] = Field(..., description="Comparison criteria")
    results: List[Dict[str, Any]] = Field(..., description="Results for each criteria")
    comparison_metrics: Dict[str, Dict[str, float]] = Field(..., description="Comparison metrics")
