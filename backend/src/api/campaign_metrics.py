"""
API endpoints pour les métriques de campagne en temps réel.
Fournit les vraies données de progression et de délivrabilité.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db_session
from ..models import Campaign, Session, PageVisit, Action, SessionStatus
from ..services.visit_verification_service import VisitVerificationService

router = APIRouter(prefix="/campaigns", tags=["campaign-metrics"])


@router.get("/{campaign_id}/real-time-metrics")
async def get_real_time_metrics(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Obtenir les métriques en temps réel d'une campagne."""
    
    # Vérifier que la campagne existe
    campaign_query = select(Campaign).where(Campaign.id == campaign_id)
    campaign_result = await db.execute(campaign_query)
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campagne non trouvée")
    
    # Statistiques des sessions
    session_stats_query = (
        select(
            Session.status,
            func.count(Session.id).label('count')
        )
        .where(Session.campaign_id == campaign_id)
        .group_by(Session.status)
    )
    session_stats_result = await db.execute(session_stats_query)
    session_counts = {row.status: row.count for row in session_stats_result.all()}
    
    # Statistiques des visites  
    visit_stats_query = (
        select(
            func.count(PageVisit.id).label('total_visits'),
            func.count(PageVisit.left_at).label('completed_visits'),
            func.avg(
                func.extract('epoch', PageVisit.left_at - PageVisit.arrived_at) * 1000
            ).label('avg_dwell_time'),
            func.sum(PageVisit.actions_count).label('total_actions')
        )
        .join(Session, PageVisit.session_id == Session.id)
        .where(Session.campaign_id == campaign_id)
    )
    visit_stats_result = await db.execute(visit_stats_query)
    visit_stats = visit_stats_result.first()
    
    # Sessions actives en temps réel
    active_sessions_query = (
        select(Session)
        .where(
            and_(
                Session.campaign_id == campaign_id,
                Session.status == SessionStatus.RUNNING
            )
        )
    )
    active_sessions_result = await db.execute(active_sessions_query)
    active_sessions = active_sessions_result.scalars().all()
    
    # Visites récentes (dernières 5 minutes)
    recent_threshold = datetime.utcnow() - timedelta(minutes=5)
    recent_visits_query = (
        select(PageVisit)
        .join(Session, PageVisit.session_id == Session.id)
        .where(
            and_(
                Session.campaign_id == campaign_id,
                PageVisit.arrived_at >= recent_threshold
            )
        )
        .order_by(PageVisit.arrived_at.desc())
        .limit(10)
    )
    recent_visits_result = await db.execute(recent_visits_query)
    recent_visits = recent_visits_result.scalars().all()
    
    # Calcul des métriques de performance
    total_sessions = campaign.total_sessions
    completed_sessions = session_counts.get('completed', 0)
    running_sessions = session_counts.get('running', 0)
    failed_sessions = session_counts.get('failed', 0)
    
    success_rate = (completed_sessions / max(total_sessions, 1)) * 100
    progress_percentage = ((completed_sessions + failed_sessions) / max(total_sessions, 1)) * 100
    
    return {
        "campaign_id": str(campaign_id),
        "campaign_name": campaign.name,
        "status": campaign.status,
        "target_url": str(campaign.target_url),
        "timestamp": datetime.utcnow().isoformat(),
        
        # Métriques principales
        "sessions": {
            "total": total_sessions,
            "completed": completed_sessions,
            "running": running_sessions,
            "failed": failed_sessions,
            "pending": max(0, total_sessions - completed_sessions - running_sessions - failed_sessions),
            "success_rate": round(success_rate, 2),
            "progress_percentage": round(progress_percentage, 2)
        },
        
        # Métriques de visites
        "visits": {
            "total_visits": visit_stats.total_visits or 0,
            "completed_visits": visit_stats.completed_visits or 0,
            "avg_dwell_time_ms": int(visit_stats.avg_dwell_time or 0),
            "total_actions": visit_stats.total_actions or 0,
            "completion_rate": round((visit_stats.completed_visits or 0) / max(visit_stats.total_visits or 1, 1) * 100, 2)
        },
        
        # Sessions actives
        "active_sessions": [
            {
                "session_id": str(session.id),
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "user_agent": session.user_agent[:50] + "..." if session.user_agent and len(session.user_agent) > 50 else session.user_agent,
                "pages_visited": session.pages_visited or 0
            }
            for session in active_sessions
        ],
        
        # Activité récente
        "recent_activity": [
            {
                "type": "visit",
                "url": visit.url,
                "timestamp": visit.arrived_at.isoformat(),
                "duration_ms": visit.dwell_time_ms,
                "actions": visit.actions_count,
                "success": visit.left_at is not None
            }
            for visit in recent_visits
        ]
    }


@router.get("/{campaign_id}/live-logs")
async def get_live_logs(
    campaign_id: UUID,
    since: Optional[datetime] = Query(None, description="Timestamp de début"),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Obtenir les logs en temps réel d'une campagne (données anonymisées)."""
    
    if not since:
        since = datetime.utcnow() - timedelta(minutes=10)
    
    # Récupérer les événements récents
    events = []
    
    # Sessions créées/démarrées/terminées
    session_events_query = (
        select(Session)
        .where(
            and_(
                Session.campaign_id == campaign_id,
                or_(
                    Session.created_at >= since,
                    Session.started_at >= since,
                    Session.completed_at >= since
                )
            )
        )
        .order_by(Session.created_at.desc())
        .limit(limit // 2)
    )
    session_events_result = await db.execute(session_events_query)
    
    for session in session_events_result.scalars().all():
        # Use the most recent timestamp available
        timestamp = session.completed_at or session.started_at or session.created_at
        
        events.append({
            "timestamp": timestamp.isoformat(),
            "type": "session",
            "action": f"Session {session.status}",
            "details": {
                "session_id": str(session.id)[:8] + "...",  # Masquer l'ID complet
                "status": session.status,
                "pages_visited": session.pages_visited or 0,
                "user_agent_type": session.user_agent.split('/')[0] if session.user_agent else "Unknown"
            }
        })
    
    # Visites de pages récentes
    visit_events_query = (
        select(PageVisit, Session)
        .join(Session, PageVisit.session_id == Session.id)
        .where(
            and_(
                Session.campaign_id == campaign_id,
                PageVisit.arrived_at >= since
            )
        )
        .order_by(PageVisit.arrived_at.desc())
        .limit(limit // 2)
    )
    visit_events_result = await db.execute(visit_events_query)
    
    for visit, session in visit_events_result.all():
        # Anonymiser l'URL (garder domaine + chemin partiel)
        from urllib.parse import urlparse
        parsed_url = urlparse(visit.url)
        safe_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path[:20]}{'...' if len(parsed_url.path) > 20 else ''}"
        
        events.append({
            "timestamp": visit.arrived_at.isoformat(),
            "type": "page_visit",
            "action": "Page visitée",
            "details": {
                "url": safe_url,
                "title": visit.title[:30] + "..." if visit.title and len(visit.title) > 30 else visit.title,
                "visit_order": visit.visit_order,
                "dwell_time_ms": visit.dwell_time_ms,
                "actions_count": visit.actions_count,
                "scroll_depth": visit.scroll_depth_percent,
                "success": visit.left_at is not None
            }
        })
    
    # Trier tous les événements par timestamp
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "campaign_id": str(campaign_id),
        "since": since.isoformat(),
        "events_count": len(events),
        "events": events[:limit]
    }


@router.get("/{campaign_id}/verification-report")
async def get_verification_report(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Obtenir un rapport de vérification de la délivrabilité."""
    
    verification_service = VisitVerificationService(db)
    
    # Statistiques de base
    campaign_stats = await verification_service.get_campaign_visit_stats(campaign_id)
    
    # Vérification des visites récentes
    recent_visits_query = (
        select(PageVisit)
        .join(Session, PageVisit.session_id == Session.id)
        .where(Session.campaign_id == campaign_id)
        .order_by(PageVisit.arrived_at.desc())
        .limit(10)
    )
    recent_visits_result = await db.execute(recent_visits_query)
    recent_visits = recent_visits_result.scalars().all()
    
    # Vérifier quelques visites pour validation
    verification_samples = []
    for visit in recent_visits[:3]:  # Vérifier les 3 dernières
        verification = await verification_service.verify_visit_authenticity(visit.id)
        verification_samples.append({
            "visit_id": str(visit.id)[:8] + "...",
            "url_domain": urlparse(visit.url).netloc,
            "confidence_score": verification.get("confidence_score", 0),
            "checks_passed": len([k for k, v in verification.get("checks", {}).items() if v.get("accessible", True) or v.get("success", True)])
        })
    
    # Surveiller les échecs
    failed_visits = await verification_service.monitor_failed_visits(campaign_id, hours_back=1)
    
    return {
        "campaign_id": str(campaign_id),
        "report_timestamp": datetime.utcnow().isoformat(),
        "deliverability_score": round(campaign_stats.get("success_rate", 0) * 100, 1),
        
        "statistics": campaign_stats,
        
        "verification_samples": verification_samples,
        "avg_confidence_score": round(sum(v["confidence_score"] for v in verification_samples) / max(len(verification_samples), 1), 3),
        
        "quality_indicators": {
            "total_visits": campaign_stats.get("total_visits", 0),
            "successful_visits": campaign_stats.get("successful_visits", 0),
            "avg_dwell_time_seconds": round((campaign_stats.get("avg_dwell_time_ms", 0) / 1000), 1),
            "total_user_actions": campaign_stats.get("total_actions", 0),
            "unique_pages": campaign_stats.get("unique_urls", 0)
        },
        
        "recent_failures": len(failed_visits),
        "failure_types": list(set(f["error_type"] for f in failed_visits))
    }


from urllib.parse import urlparse