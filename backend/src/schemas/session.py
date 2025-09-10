"""
Pydantic schemas for session API.
Defines request/response models for session endpoints.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from ..models import SessionStatus


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: UUID = Field(..., description="Session ID")
    campaign_id: UUID = Field(..., description="Campaign ID")
    persona_id: UUID = Field(..., description="Persona ID")
    status: SessionStatus = Field(..., description="Session status")
    start_url: str = Field(..., description="Starting URL")
    user_agent: str = Field(..., description="User agent string")
    viewport_width: int = Field(..., description="Viewport width")
    viewport_height: int = Field(..., description="Viewport height")
    session_duration_ms: Optional[int] = Field(None, description="Session duration in milliseconds")
    pages_visited: int = Field(..., description="Number of pages visited")
    total_actions: int = Field(..., description="Total number of actions")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, session):
        """Create response from ORM model."""
        return cls(
            id=session.id,
            campaign_id=session.campaign_id,
            persona_id=session.persona_id,
            status=session.status,
            start_url=session.start_url,
            user_agent=session.user_agent,
            viewport_width=session.viewport_width,
            viewport_height=session.viewport_height,
            session_duration_ms=session.session_duration_ms,
            pages_visited=session.pages_visited,
            total_actions=session.total_actions,
            error_message=session.error_message,
            created_at=session.created_at,
            started_at=session.started_at,
            completed_at=session.completed_at
        )


class SessionListResponse(BaseModel):
    """Schema for session list response."""
    items: List[SessionResponse] = Field(..., description="List of sessions")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
