"""
Service de vérification des visites pour s'assurer que les URLs sont réellement visitées.
Fournit des méthodes de validation et de monitoring en temps réel.
"""
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID
from urllib.parse import urlparse

import httpx
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import PageVisit, Session, Campaign
from ..database.connection import get_db_session

logger = logging.getLogger(__name__)


class VisitVerificationService:
    """Service pour vérifier et valider les visites d'URLs."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
        self.verification_cache: Dict[str, Dict[str, Any]] = {}
        
    async def verify_visit_authenticity(self, visit_id: UUID) -> Dict[str, Any]:
        """
        Vérifier l'authenticité d'une visite en analysant les données enregistrées.
        """
        try:
            # Récupérer les données de la visite
            query = (
                select(PageVisit, Session, Campaign)
                .join(Session, PageVisit.session_id == Session.id)
                .join(Campaign, Session.campaign_id == Campaign.id)
                .where(PageVisit.id == visit_id)
            )
            
            if self.db_session:
                result = await self.db_session.execute(query)
            else:
                async with get_db_session() as db_session:
                    result = await db_session.execute(query)
            
            visit_data = result.first()
            if not visit_data:
                return {"status": "error", "message": "Visite non trouvée"}
            
            visit, session, campaign = visit_data
            
            # Vérifications de cohérence
            checks = {
                "url_accessible": await self._check_url_accessibility(visit.url),
                "timing_realistic": self._check_timing_realism(visit),
                "actions_coherent": self._check_actions_coherence(visit),
                "pattern_analysis": await self._analyze_behavior_pattern(session.id),
                "http_validation": await self._validate_http_response(visit.url)
            }
            
            # Score de confiance global
            confidence_score = self._calculate_confidence_score(checks)
            
            return {
                "status": "verified",
                "visit_id": str(visit_id),
                "url": visit.url,
                "confidence_score": confidence_score,
                "checks": checks,
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "dwell_time_ms": visit.dwell_time_ms,
                    "actions_count": visit.actions_count,
                    "scroll_depth": visit.scroll_depth_percent,
                    "visit_order": visit.visit_order
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la visite {visit_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _check_url_accessibility(self, url: str) -> Dict[str, Any]:
        """Vérifier que l'URL est accessible et renvoie une réponse valide."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(url, follow_redirects=True)
                
                return {
                    "accessible": True,
                    "status_code": response.status_code,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                    "final_url": str(response.url),
                    "content_type": response.headers.get("content-type", ""),
                    "redirects": len(response.history)
                }
                
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e),
                "status_code": None
            }
    
    def _check_timing_realism(self, visit: PageVisit) -> Dict[str, Any]:
        """Analyser si les timings de la visite sont réalistes."""
        checks = {
            "has_arrival_time": visit.arrived_at is not None,
            "has_departure_time": visit.left_at is not None,
            "realistic_dwell_time": True,
            "sequential_order": True
        }
        
        if visit.dwell_time_ms:
            # Temps de séjour réaliste (entre 500ms et 30 minutes)
            checks["realistic_dwell_time"] = 500 <= visit.dwell_time_ms <= 1800000
            checks["dwell_time_ms"] = visit.dwell_time_ms
        
        # Vérifier l'ordre séquentiel des visites
        checks["visit_order"] = visit.visit_order
        checks["realistic_order"] = visit.visit_order > 0
        
        return checks
    
    def _check_actions_coherence(self, visit: PageVisit) -> Dict[str, Any]:
        """Analyser la cohérence des actions utilisateur."""
        return {
            "has_actions": visit.actions_count > 0,
            "actions_count": visit.actions_count,
            "scroll_depth": visit.scroll_depth_percent,
            "realistic_scroll": 0 <= visit.scroll_depth_percent <= 100,
            "action_density": visit.actions_count / max(visit.dwell_time_ms or 1000, 1000) * 1000 if visit.dwell_time_ms else 0
        }
    
    async def _analyze_behavior_pattern(self, session_id: UUID) -> Dict[str, Any]:
        """Analyser les patterns de comportement de la session."""
        try:
            query = (
                select(PageVisit)
                .where(PageVisit.session_id == session_id)
                .order_by(PageVisit.visit_order)
            )
            
            if self.db_session:
                result = await self.db_session.execute(query)
            else:
                async with get_db_session() as db_session:
                    result = await db_session.execute(query)
            
            visits = result.scalars().all()
            
            if len(visits) < 2:
                return {"pattern_score": 1.0, "analysis": "Pas assez de données"}
            
            # Analyser les patterns
            dwell_times = [v.dwell_time_ms for v in visits if v.dwell_time_ms]
            scroll_depths = [v.scroll_depth_percent for v in visits]
            action_counts = [v.actions_count for v in visits]
            
            analysis = {
                "visits_count": len(visits),
                "avg_dwell_time": sum(dwell_times) / len(dwell_times) if dwell_times else 0,
                "avg_scroll_depth": sum(scroll_depths) / len(scroll_depths) if scroll_depths else 0,
                "avg_actions": sum(action_counts) / len(action_counts) if action_counts else 0,
                "pattern_score": self._calculate_pattern_score(visits)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des patterns: {e}")
            return {"pattern_score": 0.5, "error": str(e)}
    
    async def _validate_http_response(self, url: str) -> Dict[str, Any]:
        """Valider la réponse HTTP complète de l'URL."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, follow_redirects=True)
                
                # Analyser le contenu
                content_size = len(response.content)
                has_html = "text/html" in response.headers.get("content-type", "")
                has_title = b"<title>" in response.content[:2048] if has_html else False
                
                return {
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "content_size": content_size,
                    "content_type": response.headers.get("content-type", ""),
                    "has_html_content": has_html,
                    "has_title_tag": has_title,
                    "server": response.headers.get("server", ""),
                    "last_modified": response.headers.get("last-modified", ""),
                    "cache_control": response.headers.get("cache-control", "")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    def _calculate_pattern_score(self, visits: List[PageVisit]) -> float:
        """Calculer un score de cohérence du pattern de navigation."""
        if len(visits) < 2:
            return 1.0
        
        scores = []
        
        # Score basé sur la progression du temps
        time_score = 1.0
        for i in range(1, len(visits)):
            if visits[i].arrived_at and visits[i-1].left_at:
                time_gap = (visits[i].arrived_at - visits[i-1].left_at).total_seconds()
                # Gap réaliste entre 0.5s et 10s
                if 0.5 <= time_gap <= 10:
                    time_score *= 1.0
                else:
                    time_score *= 0.8
        
        scores.append(time_score)
        
        # Score basé sur la variabilité des actions
        action_counts = [v.actions_count for v in visits]
        if len(set(action_counts)) > 1:  # Variabilité dans les actions
            scores.append(1.0)
        else:
            scores.append(0.7)
        
        # Score basé sur la variabilité des temps de séjour
        dwell_times = [v.dwell_time_ms for v in visits if v.dwell_time_ms]
        if len(dwell_times) > 1:
            variance = sum((t - sum(dwell_times)/len(dwell_times))**2 for t in dwell_times) / len(dwell_times)
            variability_score = min(1.0, variance / 1000000)  # Normaliser
            scores.append(variability_score)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_confidence_score(self, checks: Dict[str, Any]) -> float:
        """Calculer un score de confiance global basé sur toutes les vérifications."""
        weights = {
            "url_accessible": 0.3,
            "timing_realistic": 0.2,
            "actions_coherent": 0.2,
            "pattern_analysis": 0.2,
            "http_validation": 0.1
        }
        
        total_score = 0.0
        
        # URL accessible
        if checks["url_accessible"].get("accessible", False):
            total_score += weights["url_accessible"]
        
        # Timing réaliste
        timing = checks["timing_realistic"]
        if timing.get("realistic_dwell_time", False) and timing.get("realistic_order", False):
            total_score += weights["timing_realistic"]
        
        # Actions cohérentes
        actions = checks["actions_coherent"]
        if actions.get("has_actions", False) and actions.get("realistic_scroll", False):
            total_score += weights["actions_coherent"]
        
        # Pattern analysis
        pattern_score = checks["pattern_analysis"].get("pattern_score", 0.5)
        total_score += weights["pattern_analysis"] * pattern_score
        
        # HTTP validation
        if checks["http_validation"].get("success", False):
            total_score += weights["http_validation"]
        
        return round(total_score, 3)
    
    async def get_campaign_visit_stats(self, campaign_id: UUID) -> Dict[str, Any]:
        """Obtenir les statistiques de vérification pour une campagne."""
        try:
            query = (
                select(PageVisit, Session)
                .join(Session, PageVisit.session_id == Session.id)
                .where(Session.campaign_id == campaign_id)
            )
            
            if self.db_session:
                result = await self.db_session.execute(query)
            else:
                async with get_db_session() as db_session:
                    result = await db_session.execute(query)
            
            visits = result.all()
            
            if not visits:
                return {"total_visits": 0, "verified_visits": 0, "confidence_avg": 0.0}
            
            # Statistiques rapides
            total_visits = len(visits)
            successful_visits = len([v for v, s in visits if v.left_at is not None])
            avg_dwell_time = sum(v.dwell_time_ms or 0 for v, s in visits) / total_visits
            total_actions = sum(v.actions_count for v, s in visits)
            
            return {
                "total_visits": total_visits,
                "successful_visits": successful_visits,
                "success_rate": successful_visits / total_visits if total_visits > 0 else 0,
                "avg_dwell_time_ms": avg_dwell_time,
                "total_actions": total_actions,
                "avg_actions_per_visit": total_actions / total_visits if total_visits > 0 else 0,
                "unique_urls": len(set(v.url for v, s in visits))
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des stats: {e}")
            return {"error": str(e)}
    
    async def monitor_failed_visits(self, campaign_id: UUID, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Surveiller les visites échouées récentes."""
        try:
            since = datetime.utcnow() - timedelta(hours=hours_back)
            
            query = (
                select(PageVisit, Session)
                .join(Session, PageVisit.session_id == Session.id)
                .where(
                    and_(
                        Session.campaign_id == campaign_id,
                        PageVisit.arrived_at >= since,
                        PageVisit.left_at.is_(None),  # Visites non terminées
                        PageVisit.actions_count == 0  # Aucune action effectuée
                    )
                )
                .order_by(PageVisit.arrived_at.desc())
            )
            
            if self.db_session:
                result = await self.db_session.execute(query)
            else:
                async with get_db_session() as db_session:
                    result = await db_session.execute(query)
            
            failed_visits = []
            for visit, session in result.all():
                # Tenter de déterminer la cause de l'échec
                url_check = await self._check_url_accessibility(visit.url)
                
                error_type = "unknown"
                if not url_check.get("accessible", False):
                    if "timeout" in url_check.get("error", "").lower():
                        error_type = "timeout"
                    elif "refused" in url_check.get("error", "").lower():
                        error_type = "blocked"
                    else:
                        error_type = "network"
                elif url_check.get("status_code") == 403:
                    error_type = "forbidden"
                elif url_check.get("status_code") == 404:
                    error_type = "not_found"
                
                failed_visits.append({
                    "id": str(visit.id),
                    "url": visit.url,
                    "error_type": error_type,
                    "error_message": url_check.get("error", "Visite non terminée"),
                    "timestamp": visit.arrived_at.isoformat(),
                    "session_id": str(session.id),
                    "campaign_id": str(campaign_id),
                    "retry_count": 0  # À implémenter si nécessaire
                })
            
            return failed_visits
            
        except Exception as e:
            logger.error(f"Erreur lors de la surveillance des échecs: {e}")
            return []