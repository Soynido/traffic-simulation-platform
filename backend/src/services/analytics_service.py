"""
AnalyticsService for processing and aggregating analytics data.
Provides analytics calculations and data processing functionality.
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import (
    SessionAnalytics, CampaignAnalytics, Session, Campaign, 
    PageVisit, Action, SessionStatus, CampaignStatus
)
from ..database.connection import get_db_session


class AnalyticsService:
    """Service for analytics data processing and aggregation."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """Initialize AnalyticsService with optional database session."""
        self.db_session = db_session
    
    async def create_session_analytics(self, session_id: UUID) -> Optional[SessionAnalytics]:
        """Create analytics for a completed session."""
        session = await self._get_session_with_details(session_id)
        if not session or session.status != SessionStatus.COMPLETED:
            return None
        
        # Calculate metrics
        metrics = await self._calculate_session_metrics(session)
        
        # Create analytics record
        analytics_data = {
            'session_id': session_id,
            'campaign_id': session.campaign_id,
            'persona_id': session.persona_id,
            **metrics
        }
        
        analytics = SessionAnalytics.from_dict(analytics_data)
        
        if self.db_session:
            self.db_session.add(analytics)
            await self.db_session.commit()
            await self.db_session.refresh(analytics)
        else:
            async with get_db_session() as db_session:
                db_session.add(analytics)
                await db_session.commit()
                await db_session.refresh(analytics)
        
        return analytics
    
    async def create_campaign_analytics(self, campaign_id: UUID) -> Optional[CampaignAnalytics]:
        """Create analytics for a campaign."""
        campaign = await self._get_campaign_with_sessions(campaign_id)
        if not campaign:
            return None
        
        # Get all session analytics for this campaign
        session_analytics = await self._get_session_analytics_by_campaign(campaign_id)
        
        if not session_analytics:
            return None
        
        # Calculate campaign metrics
        metrics = await self._calculate_campaign_metrics(campaign, session_analytics)
        
        # Create or update analytics record
        analytics_data = {
            'campaign_id': campaign_id,
            **metrics
        }
        
        # Check if analytics already exist
        existing_analytics = await self._get_campaign_analytics(campaign_id)
        
        if existing_analytics:
            # Update existing
            for key, value in analytics_data.items():
                if key != 'campaign_id':
                    setattr(existing_analytics, key, value)
            existing_analytics.update_timestamps()
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(existing_analytics)
            else:
                async with get_db_session() as db_session:
                    db_session.add(existing_analytics)
                    await db_session.commit()
                    await db_session.refresh(existing_analytics)
            
            return existing_analytics
        else:
            # Create new
            analytics = CampaignAnalytics.from_dict(analytics_data)
            
            if self.db_session:
                self.db_session.add(analytics)
                await self.db_session.commit()
                await self.db_session.refresh(analytics)
            else:
                async with get_db_session() as db_session:
                    db_session.add(analytics)
                    await db_session.commit()
                    await db_session.refresh(analytics)
            
            return analytics
    
    async def get_session_analytics(self, session_id: UUID) -> Optional[SessionAnalytics]:
        """Get session analytics by session ID."""
        query = (
            select(SessionAnalytics)
            .options(
                selectinload(SessionAnalytics.session),
                selectinload(SessionAnalytics.campaign),
                selectinload(SessionAnalytics.persona)
            )
            .where(SessionAnalytics.session_id == session_id)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalar_one_or_none()
    
    async def get_campaign_analytics(self, campaign_id: UUID) -> Optional[CampaignAnalytics]:
        """Get campaign analytics by campaign ID."""
        query = (
            select(CampaignAnalytics)
            .options(selectinload(CampaignAnalytics.campaign))
            .where(CampaignAnalytics.campaign_id == campaign_id)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalar_one_or_none()
    
    async def get_analytics_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        campaign_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get analytics summary for specified criteria."""
        # Get session analytics
        session_analytics = await self._get_session_analytics_filtered(
            start_date, end_date, campaign_id
        )
        
        if not session_analytics:
            return {
                'total_sessions': 0,
                'completed_sessions': 0,
                'failed_sessions': 0,
                'success_rate': 0.0,
                'avg_session_duration_ms': 0,
                'avg_pages_per_session': 0.0,
                'avg_actions_per_session': 0.0,
                'avg_rhythm_score': 0.0,
                'detection_risk_score': 0.0
            }
        
        # Calculate summary metrics
        total_sessions = len(session_analytics)
        completed_sessions = sum(1 for sa in session_analytics if sa.pages_visited > 0)
        failed_sessions = total_sessions - completed_sessions
        success_rate = completed_sessions / total_sessions if total_sessions > 0 else 0.0
        
        avg_duration = statistics.mean([sa.total_duration_ms for sa in session_analytics])
        avg_pages = statistics.mean([sa.pages_visited for sa in session_analytics])
        avg_actions = statistics.mean([sa.total_actions for sa in session_analytics])
        
        rhythm_scores = [sa.rhythm_score for sa in session_analytics if sa.rhythm_score is not None]
        avg_rhythm = statistics.mean(rhythm_scores) if rhythm_scores else 0.0
        
        detection_risk_scores = [sa.action_variance for sa in session_analytics if sa.action_variance is not None]
        avg_detection_risk = statistics.mean(detection_risk_scores) if detection_risk_scores else 0.0
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'failed_sessions': failed_sessions,
            'success_rate': success_rate,
            'avg_session_duration_ms': avg_duration,
            'avg_pages_per_session': avg_pages,
            'avg_actions_per_session': avg_actions,
            'avg_rhythm_score': avg_rhythm,
            'detection_risk_score': avg_detection_risk
        }
    
    async def _get_session_with_details(self, session_id: UUID) -> Optional[Session]:
        """Get session with all related data."""
        query = (
            select(Session)
            .options(
                selectinload(Session.page_visits).selectinload(PageVisit.actions),
                selectinload(Session.campaign),
                selectinload(Session.persona)
            )
            .where(Session.id == session_id)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalar_one_or_none()
    
    async def _get_campaign_with_sessions(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign with all sessions."""
        query = (
            select(Campaign)
            .options(selectinload(Campaign.sessions))
            .where(Campaign.id == campaign_id)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalar_one_or_none()
    
    async def _get_session_analytics_by_campaign(self, campaign_id: UUID) -> List[SessionAnalytics]:
        """Get all session analytics for a campaign."""
        query = select(SessionAnalytics).where(SessionAnalytics.campaign_id == campaign_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalars().all()
    
    async def _get_campaign_analytics(self, campaign_id: UUID) -> Optional[CampaignAnalytics]:
        """Get campaign analytics if they exist."""
        query = select(CampaignAnalytics).where(CampaignAnalytics.campaign_id == campaign_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalar_one_or_none()
    
    async def _get_session_analytics_filtered(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        campaign_id: Optional[UUID] = None
    ) -> List[SessionAnalytics]:
        """Get session analytics with filters."""
        query = select(SessionAnalytics)
        
        conditions = []
        if start_date:
            conditions.append(SessionAnalytics.created_at >= start_date)
        if end_date:
            conditions.append(SessionAnalytics.created_at <= end_date)
        if campaign_id:
            conditions.append(SessionAnalytics.campaign_id == campaign_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(SessionAnalytics.created_at.desc())
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalars().all()
    
    async def _calculate_session_metrics(self, session: Session) -> Dict[str, Any]:
        """Calculate metrics for a session."""
        page_visits = session.page_visits
        actions = []
        for page_visit in page_visits:
            actions.extend(page_visit.actions)
        
        # Basic metrics
        total_duration_ms = session.session_duration_ms or 0
        pages_visited = len(page_visits)
        total_actions = len(actions)
        
        # Calculate dwell times
        dwell_times = []
        for page_visit in page_visits:
            if page_visit.dwell_time_ms:
                dwell_times.append(page_visit.dwell_time_ms)
        
        avg_dwell_time = statistics.mean(dwell_times) if dwell_times else None
        median_dwell_time = statistics.median(dwell_times) if dwell_times else None
        
        # Calculate bounce rate
        bounce_rate = 1.0 if pages_visited <= 1 else 0.0
        
        # Calculate actions per page
        actions_per_page = total_actions / pages_visited if pages_visited > 0 else 0
        
        # Calculate scroll engagement
        scroll_depths = [pv.scroll_depth_percent for pv in page_visits]
        scroll_engagement = statistics.mean(scroll_depths) / 100 if scroll_depths else 0
        
        # Calculate rhythm score
        action_timestamps = [action.timestamp for action in actions if action.timestamp]
        rhythm_score = self._calculate_rhythm_score(action_timestamps)
        
        # Calculate action variance
        action_durations = [action.duration_ms for action in actions if action.duration_ms]
        action_variance = statistics.variance(action_durations) if len(action_durations) > 1 else 0
        
        # Calculate pause distribution
        pause_distribution = self._calculate_pause_distribution(action_timestamps)
        
        return {
            'total_duration_ms': total_duration_ms,
            'avg_page_dwell_time_ms': avg_dwell_time,
            'median_page_dwell_time_ms': median_dwell_time,
            'pages_visited': pages_visited,
            'navigation_depth': pages_visited,  # Simplified
            'bounce_rate': bounce_rate,
            'total_actions': total_actions,
            'actions_per_page': actions_per_page,
            'click_through_rate': 0.0,  # Simplified
            'scroll_engagement': scroll_engagement,
            'action_variance': action_variance,
            'rhythm_score': rhythm_score,
            'pause_distribution': pause_distribution
        }
    
    async def _calculate_campaign_metrics(
        self, 
        campaign: Campaign, 
        session_analytics: List[SessionAnalytics]
    ) -> Dict[str, Any]:
        """Calculate metrics for a campaign."""
        total_sessions = len(session_analytics)
        completed_sessions = sum(1 for sa in session_analytics if sa.pages_visited > 0)
        failed_sessions = total_sessions - completed_sessions
        success_rate = completed_sessions / total_sessions if total_sessions > 0 else 0.0
        
        # Calculate averages
        durations = [sa.total_duration_ms for sa in session_analytics if sa.total_duration_ms]
        avg_duration = statistics.mean(durations) if durations else None
        
        pages = [sa.pages_visited for sa in session_analytics]
        avg_pages = statistics.mean(pages) if pages else None
        
        actions = [sa.total_actions for sa in session_analytics]
        avg_actions = statistics.mean(actions) if actions else None
        
        # Calculate quality metrics
        rhythm_scores = [sa.rhythm_score for sa in session_analytics if sa.rhythm_score is not None]
        avg_rhythm = statistics.mean(rhythm_scores) if rhythm_scores else None
        
        action_variances = [sa.action_variance for sa in session_analytics if sa.action_variance is not None]
        behavioral_variance = statistics.mean(action_variances) if action_variances else None
        
        # Calculate detection risk
        detection_risk = self._calculate_detection_risk(rhythm_scores, action_variances)
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'failed_sessions': failed_sessions,
            'success_rate': success_rate,
            'avg_session_duration_ms': avg_duration,
            'avg_pages_per_session': avg_pages,
            'avg_actions_per_session': avg_actions,
            'avg_rhythm_score': avg_rhythm,
            'behavioral_variance': behavioral_variance,
            'detection_risk_score': detection_risk,
            'total_runtime_ms': None,  # Would need to track this separately
            'avg_cpu_usage': None,  # Would need to track this separately
            'peak_memory_mb': None  # Would need to track this separately
        }
    
    def _calculate_rhythm_score(self, timestamps: List[datetime]) -> Optional[float]:
        """Calculate rhythm score from action timestamps."""
        if len(timestamps) < 3:
            return None
        
        # Sort timestamps
        timestamps.sort()
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return None
        
        # Calculate coefficient of variation
        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return 0.0
        
        std_dev = statistics.stdev(intervals) if len(intervals) > 1 else 0
        cv = std_dev / mean_interval
        
        # Convert to 0-1 scale where 1 is most human-like
        return min(1.0, max(0.0, cv))
    
    def _calculate_pause_distribution(self, timestamps: List[datetime]) -> Dict[str, float]:
        """Calculate pause distribution from action timestamps."""
        if len(timestamps) < 2:
            return {}
        
        timestamps.sort()
        intervals = []
        
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return {}
        
        # Categorize pauses
        short_pauses = sum(1 for i in intervals if 0 <= i < 1)
        medium_pauses = sum(1 for i in intervals if 1 <= i < 5)
        long_pauses = sum(1 for i in intervals if i >= 5)
        
        total = len(intervals)
        
        return {
            'short_pauses': short_pauses / total if total > 0 else 0,
            'medium_pauses': medium_pauses / total if total > 0 else 0,
            'long_pauses': long_pauses / total if total > 0 else 0
        }
    
    def _calculate_detection_risk(
        self, 
        rhythm_scores: List[float], 
        action_variances: List[float]
    ) -> Optional[float]:
        """Calculate detection risk score."""
        all_scores = rhythm_scores + action_variances
        
        if not all_scores:
            return None
        
        # Calculate average score
        avg_score = statistics.mean(all_scores)
        
        # Invert score so lower human-like behavior = higher detection risk
        return max(0.0, min(1.0, 1.0 - avg_score))
