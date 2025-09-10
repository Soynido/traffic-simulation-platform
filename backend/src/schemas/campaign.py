"""
Pydantic schemas for campaign API.
Defines request/response models for campaign endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, validator, HttpUrl

from ..models import CampaignStatus


class CampaignBase(BaseModel):
    """Base campaign schema with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    target_url: HttpUrl = Field(..., description="Target URL for simulation")
    total_sessions: int = Field(..., gt=0, description="Total number of sessions to run")
    concurrent_sessions: int = Field(10, gt=0, description="Number of concurrent sessions")
    persona_id: UUID = Field(..., description="Persona ID to use for simulation")
    rate_limit_delay_ms: int = Field(1000, ge=100, description="Delay between requests in milliseconds")
    user_agent_rotation: bool = Field(True, description="Whether to rotate user agents")
    respect_robots_txt: bool = Field(True, description="Whether to respect robots.txt")
    
    @validator('concurrent_sessions')
    def validate_concurrent_sessions(cls, v, values):
        """Validate that concurrent sessions <= total sessions."""
        if 'total_sessions' in values and v > values['total_sessions']:
            raise ValueError('concurrent_sessions must be <= total_sessions')
        return v


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""
    pass


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    target_url: Optional[HttpUrl] = Field(None, description="Target URL for simulation")
    total_sessions: Optional[int] = Field(None, gt=0, description="Total number of sessions to run")
    concurrent_sessions: Optional[int] = Field(None, gt=0, description="Number of concurrent sessions")
    persona_id: Optional[UUID] = Field(None, description="Persona ID to use for simulation")
    rate_limit_delay_ms: Optional[int] = Field(None, ge=100, description="Delay between requests in milliseconds")
    user_agent_rotation: Optional[bool] = Field(None, description="Whether to rotate user agents")
    respect_robots_txt: Optional[bool] = Field(None, description="Whether to respect robots.txt")
    
    @validator('concurrent_sessions')
    def validate_concurrent_sessions(cls, v, values):
        """Validate that concurrent sessions <= total sessions."""
        if v is not None and 'total_sessions' in values and values['total_sessions'] is not None:
            if v > values['total_sessions']:
                raise ValueError('concurrent_sessions must be <= total_sessions')
        return v


class CampaignResponse(CampaignBase):
    """Schema for campaign response."""
    id: UUID = Field(..., description="Campaign ID")
    status: CampaignStatus = Field(..., description="Campaign status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, campaign):
        """Create response from ORM model."""
        return cls(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            target_url=campaign.target_url,
            total_sessions=campaign.total_sessions,
            concurrent_sessions=campaign.concurrent_sessions,
            persona_id=campaign.persona_id,
            rate_limit_delay_ms=campaign.rate_limit_delay_ms,
            user_agent_rotation=campaign.user_agent_rotation,
            respect_robots_txt=campaign.respect_robots_txt,
            status=campaign.status,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            started_at=campaign.started_at,
            completed_at=campaign.completed_at
        )


class CampaignListResponse(BaseModel):
    """Schema for campaign list response."""
    items: List[CampaignResponse] = Field(..., description="List of campaigns")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")


class CampaignStartResponse(BaseModel):
    """Schema for campaign start/pause/resume response."""
    campaign_id: UUID = Field(..., description="Campaign ID")
    status: str = Field(..., description="Campaign status")
    message: str = Field(..., description="Response message")


class CampaignStatusResponse(BaseModel):
    """Schema for campaign status response."""
    campaign_id: str = Field(..., description="Campaign ID")
    status: str = Field(..., description="Campaign status")
    total_sessions: int = Field(..., description="Total number of sessions")
    session_counts: Dict[str, int] = Field(..., description="Session counts by status")
    success_rate: float = Field(..., description="Success rate")
    started_at: Optional[str] = Field(None, description="Start timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    queued_jobs: int = Field(..., description="Number of queued jobs")
