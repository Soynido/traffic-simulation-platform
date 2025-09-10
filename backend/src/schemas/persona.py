"""
Pydantic schemas for persona API.
Defines request/response models for persona endpoints.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, validator


class PersonaBase(BaseModel):
    """Base persona schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Persona name")
    description: Optional[str] = Field(None, description="Persona description")
    session_duration_min: int = Field(..., gt=0, description="Minimum session duration in seconds")
    session_duration_max: int = Field(..., gt=0, description="Maximum session duration in seconds")
    pages_min: int = Field(..., gt=0, description="Minimum pages to visit")
    pages_max: int = Field(..., gt=0, description="Maximum pages to visit")
    actions_per_page_min: int = Field(1, ge=1, description="Minimum actions per page")
    actions_per_page_max: int = Field(10, ge=1, description="Maximum actions per page")
    scroll_probability: Decimal = Field(0.8, ge=0, le=1, description="Probability of scrolling")
    click_probability: Decimal = Field(0.6, ge=0, le=1, description="Probability of clicking")
    typing_probability: Decimal = Field(0.1, ge=0, le=1, description="Probability of typing")
    
    @validator('session_duration_max')
    def validate_duration_range(cls, v, values):
        """Validate that max duration is >= min duration."""
        if 'session_duration_min' in values and v < values['session_duration_min']:
            raise ValueError('session_duration_max must be >= session_duration_min')
        return v
    
    @validator('pages_max')
    def validate_pages_range(cls, v, values):
        """Validate that max pages is >= min pages."""
        if 'pages_min' in values and v < values['pages_min']:
            raise ValueError('pages_max must be >= pages_min')
        return v
    
    @validator('actions_per_page_max')
    def validate_actions_range(cls, v, values):
        """Validate that max actions is >= min actions."""
        if 'actions_per_page_min' in values and v < values['actions_per_page_min']:
            raise ValueError('actions_per_page_max must be >= actions_per_page_min')
        return v


class PersonaCreate(PersonaBase):
    """Schema for creating a persona."""
    pass


class PersonaUpdate(BaseModel):
    """Schema for updating a persona."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Persona name")
    description: Optional[str] = Field(None, description="Persona description")
    session_duration_min: Optional[int] = Field(None, gt=0, description="Minimum session duration in seconds")
    session_duration_max: Optional[int] = Field(None, gt=0, description="Maximum session duration in seconds")
    pages_min: Optional[int] = Field(None, gt=0, description="Minimum pages to visit")
    pages_max: Optional[int] = Field(None, gt=0, description="Maximum pages to visit")
    actions_per_page_min: Optional[int] = Field(None, ge=1, description="Minimum actions per page")
    actions_per_page_max: Optional[int] = Field(None, ge=1, description="Maximum actions per page")
    scroll_probability: Optional[Decimal] = Field(None, ge=0, le=1, description="Probability of scrolling")
    click_probability: Optional[Decimal] = Field(None, ge=0, le=1, description="Probability of clicking")
    typing_probability: Optional[Decimal] = Field(None, ge=0, le=1, description="Probability of typing")
    
    @validator('session_duration_max')
    def validate_duration_range(cls, v, values):
        """Validate that max duration is >= min duration."""
        if v is not None and 'session_duration_min' in values and values['session_duration_min'] is not None:
            if v < values['session_duration_min']:
                raise ValueError('session_duration_max must be >= session_duration_min')
        return v
    
    @validator('pages_max')
    def validate_pages_range(cls, v, values):
        """Validate that max pages is >= min pages."""
        if v is not None and 'pages_min' in values and values['pages_min'] is not None:
            if v < values['pages_min']:
                raise ValueError('pages_max must be >= pages_min')
        return v
    
    @validator('actions_per_page_max')
    def validate_actions_range(cls, v, values):
        """Validate that max actions is >= min actions."""
        if v is not None and 'actions_per_page_min' in values and values['actions_per_page_min'] is not None:
            if v < values['actions_per_page_min']:
                raise ValueError('actions_per_page_max must be >= actions_per_page_min')
        return v


class PersonaResponse(PersonaBase):
    """Schema for persona response."""
    id: UUID = Field(..., description="Persona ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, persona):
        """Create response from ORM model."""
        return cls(
            id=persona.id,
            name=persona.name,
            description=persona.description,
            session_duration_min=persona.session_duration_min,
            session_duration_max=persona.session_duration_max,
            pages_min=persona.pages_min,
            pages_max=persona.pages_max,
            actions_per_page_min=persona.actions_per_page_min,
            actions_per_page_max=persona.actions_per_page_max,
            scroll_probability=persona.scroll_probability,
            click_probability=persona.click_probability,
            typing_probability=persona.typing_probability,
            created_at=persona.created_at,
            updated_at=persona.updated_at
        )


class PersonaListResponse(BaseModel):
    """Schema for persona list response."""
    items: List[PersonaResponse] = Field(..., description="List of personas")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
