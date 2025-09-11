from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any
import logging

from ..database.connection import get_db_session
from ..models.analytics import CampaignAnalytics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/campaigns", response_model=List[CampaignAnalytics])
async def get_campaign_analytics(
    db_session: AsyncSession = Depends(get_db_session)
) -> List[CampaignAnalytics]:
    """Récupère les statistiques analytiques des campagnes."""
    try:
        query = text("""
            SELECT 
                campaign_id,
                COUNT(*) AS total_sessions,
                ROUND(AVG(session_duration_ms)/1000, 2) AS avg_duration_s,
                ROUND(AVG(pages_visited), 2) AS avg_pages,
                ROUND(AVG(total_actions), 2) AS avg_actions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) AS successful_sessions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) AS failed_sessions
            FROM sessions 
            GROUP BY campaign_id 
            ORDER BY total_sessions DESC 
            LIMIT 20
        """)
        
        result = await db_session.execute(query)
        rows = result.fetchall()
        
        analytics = []
        for row in rows:
            analytics.append(CampaignAnalytics(
                campaign_id=str(row.campaign_id),
                total_sessions=row.total_sessions,
                avg_duration_s=float(row.avg_duration_s) if row.avg_duration_s else 0.0,
                avg_pages=float(row.avg_pages) if row.avg_pages else 0.0,
                avg_actions=float(row.avg_actions) if row.avg_actions else 0.0,
                successful_sessions=row.successful_sessions,
                failed_sessions=row.failed_sessions
            ))
        
        logger.info(f"Retrieved analytics for {len(analytics)} campaigns")
        return analytics
        
    except Exception as e:
        logger.error(f"Error retrieving campaign analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve campaign analytics")


@router.get("/campaigns/{campaign_id}/details", response_model=List[Dict[str, Any]])
async def get_campaign_details(
    campaign_id: str,
    db_session: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """Récupère les détails des pages visitées pour une campagne spécifique."""
    try:
        query = text("""
            SELECT 
                s.id AS session_id,
                s.status,
                s.session_duration_ms,
                s.pages_visited,
                s.total_actions,
                pv.url,
                pv.title,
                pv.actions_count,
                pv.scroll_depth_percent,
                pv.arrived_at,
                pv.left_at
            FROM sessions s
            LEFT JOIN page_visits pv ON s.id = pv.session_id
            WHERE s.campaign_id = :campaign_id
            ORDER BY s.created_at DESC, pv.visit_order ASC
            LIMIT 50
        """)
        
        result = await db_session.execute(query, {"campaign_id": campaign_id})
        rows = result.fetchall()
        
        details = []
        for row in rows:
            details.append({
                "session_id": str(row.session_id),
                "status": row.status,
                "session_duration_ms": row.session_duration_ms,
                "pages_visited": row.pages_visited,
                "total_actions": row.total_actions,
                "url": row.url,
                "title": row.title,
                "actions_count": row.actions_count,
                "scroll_depth_percent": row.scroll_depth_percent,
                "arrived_at": row.arrived_at.isoformat() if row.arrived_at else None,
                "left_at": row.left_at.isoformat() if row.left_at else None
            })
        
        logger.info(f"Retrieved {len(details)} details for campaign {campaign_id}")
        return details
        
    except Exception as e:
        logger.error(f"Error retrieving campaign details for {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve campaign details")


@router.get("/campaigns/{campaign_id}/summary", response_model=Dict[str, Any])
async def get_campaign_summary(
    campaign_id: str,
    db_session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Récupère un résumé complet d'une campagne."""
    try:
        # Statistiques générales
        stats_query = text("""
            SELECT 
                COUNT(*) AS total_sessions,
                ROUND(AVG(session_duration_ms)/1000, 2) AS avg_duration_s,
                ROUND(AVG(pages_visited), 2) AS avg_pages,
                ROUND(AVG(total_actions), 2) AS avg_actions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) AS successful_sessions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) AS failed_sessions,
                MIN(created_at) AS first_session,
                MAX(created_at) AS last_session
            FROM sessions 
            WHERE campaign_id = :campaign_id
        """)
        
        result = await db_session.execute(stats_query, {"campaign_id": campaign_id})
        stats_row = result.fetchone()
        
        if not stats_row:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Pages les plus visitées
        pages_query = text("""
            SELECT 
                pv.url,
                pv.title,
                COUNT(*) AS visit_count,
                ROUND(AVG(pv.actions_count), 2) AS avg_actions,
                ROUND(AVG(pv.scroll_depth_percent), 2) AS avg_scroll_depth
            FROM page_visits pv
            JOIN sessions s ON pv.session_id = s.id
            WHERE s.campaign_id = :campaign_id
            GROUP BY pv.url, pv.title
            ORDER BY visit_count DESC
            LIMIT 10
        """)
        
        result = await db_session.execute(pages_query, {"campaign_id": campaign_id})
        pages_rows = result.fetchall()
        
        top_pages = []
        for row in pages_rows:
            top_pages.append({
                "url": row.url,
                "title": row.title,
                "visit_count": row.visit_count,
                "avg_actions": float(row.avg_actions) if row.avg_actions else 0.0,
                "avg_scroll_depth": float(row.avg_scroll_depth) if row.avg_scroll_depth else 0.0
            })
        
        summary = {
            "campaign_id": campaign_id,
            "total_sessions": stats_row.total_sessions,
            "avg_duration_s": float(stats_row.avg_duration_s) if stats_row.avg_duration_s else 0.0,
            "avg_pages": float(stats_row.avg_pages) if stats_row.avg_pages else 0.0,
            "avg_actions": float(stats_row.avg_actions) if stats_row.avg_actions else 0.0,
            "successful_sessions": stats_row.successful_sessions,
            "failed_sessions": stats_row.failed_sessions,
            "success_rate": round(stats_row.successful_sessions / stats_row.total_sessions * 100, 2) if stats_row.total_sessions > 0 else 0.0,
            "first_session": stats_row.first_session.isoformat() if stats_row.first_session else None,
            "last_session": stats_row.last_session.isoformat() if stats_row.last_session else None,
            "top_pages": top_pages
        }
        
        logger.info(f"Generated summary for campaign {campaign_id}")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating campaign summary for {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate campaign summary")