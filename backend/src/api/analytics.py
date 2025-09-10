"""
Analytics API endpoints.
Provides REST API for analytics data.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..services import AnalyticsService
from ..database.connection import get_db_session
from ..schemas.analytics import (
    CampaignAnalyticsResponse, SessionAnalyticsResponse, 
    AnalyticsSummaryResponse, ComparisonRequest, ComparisonResponse
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/campaigns/{campaign_id}", response_model=CampaignAnalyticsResponse)
async def get_campaign_analytics(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get campaign analytics by campaign ID."""
    service = AnalyticsService(db)
    
    analytics = await service.get_campaign_analytics(campaign_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign analytics not found"
        )
    
    return CampaignAnalyticsResponse.from_orm(analytics)


@router.get("/sessions/{session_id}", response_model=SessionAnalyticsResponse)
async def get_session_analytics(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get session analytics by session ID."""
    service = AnalyticsService(db)
    
    analytics = await service.get_session_analytics(session_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session analytics not found"
        )
    
    return SessionAnalyticsResponse.from_orm(analytics)


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    campaign_id: Optional[UUID] = Query(None, description="Campaign ID filter"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get analytics summary for specified criteria."""
    service = AnalyticsService(db)
    
    summary = await service.get_analytics_summary(
        start_date=start_date,
        end_date=end_date,
        campaign_id=campaign_id
    )
    
    return AnalyticsSummaryResponse(**summary)


@router.post("/compare", response_model=ComparisonResponse)
async def compare_analytics(
    comparison_request: ComparisonRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Compare analytics between different criteria."""
    service = AnalyticsService(db)
    
    # Get analytics for each criteria
    results = []
    
    for criteria in comparison_request.criteria:
        summary = await service.get_analytics_summary(
            start_date=criteria.start_date,
            end_date=criteria.end_date,
            campaign_id=criteria.campaign_id
        )
        
        results.append({
            'name': criteria.name,
            'criteria': criteria.dict(),
            'summary': summary
        })
    
    # Calculate comparison metrics
    comparison_metrics = _calculate_comparison_metrics(results)
    
    return ComparisonResponse(
        criteria=comparison_request.criteria,
        results=results,
        comparison_metrics=comparison_metrics
    )


@router.post("/campaigns/{campaign_id}/generate", response_model=CampaignAnalyticsResponse)
async def generate_campaign_analytics(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Generate analytics for a campaign."""
    service = AnalyticsService(db)
    
    # Generate analytics
    analytics = await service.create_campaign_analytics(campaign_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found or no sessions to analyze"
        )
    
    return CampaignAnalyticsResponse.from_orm(analytics)


@router.post("/sessions/{session_id}/generate", response_model=SessionAnalyticsResponse)
async def generate_session_analytics(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Generate analytics for a session."""
    service = AnalyticsService(db)
    
    # Generate analytics
    analytics = await service.create_session_analytics(session_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or not completed"
        )
    
    return SessionAnalyticsResponse.from_orm(analytics)


def _calculate_comparison_metrics(results: List[dict]) -> dict:
    """Calculate comparison metrics between results."""
    if len(results) < 2:
        return {}
    
    # Extract key metrics for comparison
    metrics = ['success_rate', 'avg_session_duration_ms', 'avg_pages_per_session', 
               'avg_actions_per_session', 'avg_rhythm_score', 'detection_risk_score']
    
    comparison = {}
    
    for metric in metrics:
        values = []
        for result in results:
            if metric in result['summary']:
                values.append(result['summary'][metric])
        
        if len(values) >= 2:
            comparison[metric] = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'variance': _calculate_variance(values)
            }
    
    return comparison


def _calculate_variance(values: List[float]) -> float:
    """Calculate variance of a list of values."""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance
