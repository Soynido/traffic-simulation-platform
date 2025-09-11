from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CampaignAnalytics(BaseModel):
    """Modèle pour les statistiques analytiques d'une campagne."""
    campaign_id: str
    total_sessions: int
    avg_duration_s: float
    avg_pages: float
    avg_actions: float
    successful_sessions: int
    failed_sessions: int

    class Config:
        from_attributes = True


class PageVisitDetail(BaseModel):
    """Modèle pour les détails d'une visite de page."""
    session_id: str
    status: str
    session_duration_ms: Optional[int]
    pages_visited: Optional[int]
    total_actions: Optional[int]
    url: Optional[str]
    title: Optional[str]
    actions_count: Optional[int]
    scroll_depth_percent: Optional[int]
    arrived_at: Optional[str]
    left_at: Optional[str]


class TopPage(BaseModel):
    """Modèle pour les pages les plus visitées."""
    url: str
    title: Optional[str]
    visit_count: int
    avg_actions: float
    avg_scroll_depth: float


class CampaignSummary(BaseModel):
    """Modèle pour le résumé complet d'une campagne."""
    campaign_id: str
    total_sessions: int
    avg_duration_s: float
    avg_pages: float
    avg_actions: float
    successful_sessions: int
    failed_sessions: int
    success_rate: float
    first_session: Optional[str]
    last_session: Optional[str]
    top_pages: List[TopPage]
