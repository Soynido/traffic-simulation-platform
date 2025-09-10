"""
Schemas package for traffic simulation platform.
Contains all Pydantic models for API requests and responses.
"""

from .persona import PersonaCreate, PersonaUpdate, PersonaResponse, PersonaListResponse
from .campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse,
    CampaignStartResponse, CampaignStatusResponse
)
from .session import SessionResponse, SessionListResponse
from .analytics import (
    SessionAnalyticsResponse, CampaignAnalyticsResponse, AnalyticsSummaryResponse,
    ComparisonRequest, ComparisonResponse
)

__all__ = [
    # Persona schemas
    'PersonaCreate', 'PersonaUpdate', 'PersonaResponse', 'PersonaListResponse',
    
    # Campaign schemas
    'CampaignCreate', 'CampaignUpdate', 'CampaignResponse', 'CampaignListResponse',
    'CampaignStartResponse', 'CampaignStatusResponse',
    
    # Session schemas
    'SessionResponse', 'SessionListResponse',
    
    # Analytics schemas
    'SessionAnalyticsResponse', 'CampaignAnalyticsResponse', 'AnalyticsSummaryResponse',
    'ComparisonRequest', 'ComparisonResponse'
]
