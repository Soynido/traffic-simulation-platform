"""
SimulationOrchestrator for managing simulation jobs and queue.
Provides job queue management and simulation coordination.
"""
import asyncio
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Campaign, Session, CampaignStatus, SessionStatus
from ..database.connection import get_db_session


class SimulationOrchestrator:
    """Orchestrator for managing simulation jobs and queue."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """Initialize SimulationOrchestrator with optional database session."""
        self.db_session = db_session
        self.active_workers: Dict[str, Dict[str, Any]] = {}
        self.job_queue: List[Dict[str, Any]] = []
        self.max_concurrent_sessions = 10
    
    async def start_campaign_simulation(self, campaign_id: UUID) -> bool:
        """Start simulation for a campaign."""
        campaign = await self._get_campaign_with_persona(campaign_id)
        if not campaign:
            return False
        
        if campaign.status != CampaignStatus.PENDING:
            return False
        
        # Update campaign status
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = datetime.utcnow()
        
        if self.db_session:
            await self.db_session.commit()
        else:
            async with get_db_session() as session:
                session.add(campaign)
                await session.commit()
        
        # Create sessions for the campaign
        await self._create_campaign_sessions(campaign)
        
        # Start processing sessions
        await self._process_campaign_sessions(campaign_id)
        
        return True
    
    async def pause_campaign_simulation(self, campaign_id: UUID) -> bool:
        """Pause simulation for a campaign."""
        campaign = await self._get_campaign(campaign_id)
        if not campaign or campaign.status != CampaignStatus.RUNNING:
            return False
        
        # Update campaign status
        campaign.status = CampaignStatus.PAUSED
        
        if self.db_session:
            await self.db_session.commit()
        else:
            async with get_db_session() as session:
                session.add(campaign)
                await session.commit()
        
        # Remove campaign sessions from queue
        self.job_queue = [job for job in self.job_queue if job.get('campaign_id') != campaign_id]
        
        return True
    
    async def resume_campaign_simulation(self, campaign_id: UUID) -> bool:
        """Resume simulation for a campaign."""
        campaign = await self._get_campaign(campaign_id)
        if not campaign or campaign.status != CampaignStatus.PAUSED:
            return False
        
        # Update campaign status
        campaign.status = CampaignStatus.RUNNING
        
        if self.db_session:
            await self.db_session.commit()
        else:
            async with get_db_session() as session:
                session.add(campaign)
                await session.commit()
        
        # Resume processing sessions
        await self._process_campaign_sessions(campaign_id)
        
        return True
    
    async def stop_campaign_simulation(self, campaign_id: UUID) -> bool:
        """Stop simulation for a campaign."""
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return False
        
        # Update campaign status
        campaign.status = CampaignStatus.COMPLETED
        campaign.completed_at = datetime.utcnow()
        
        if self.db_session:
            await self.db_session.commit()
        else:
            async with get_db_session() as session:
                session.add(campaign)
                await session.commit()
        
        # Remove campaign sessions from queue
        self.job_queue = [job for job in self.job_queue if job.get('campaign_id') != campaign_id]
        
        return True
    
    async def get_campaign_status(self, campaign_id: UUID) -> Optional[Dict[str, Any]]:
        """Get campaign simulation status."""
        campaign = await self._get_campaign_with_sessions(campaign_id)
        if not campaign:
            return None
        
        # Count sessions by status
        session_counts = {
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0,
            'timeout': 0
        }
        
        for session in campaign.sessions:
            session_counts[session.status.value] += 1
        
        total_sessions = len(campaign.sessions)
        completed_sessions = session_counts['completed']
        success_rate = completed_sessions / total_sessions if total_sessions > 0 else 0.0
        
        return {
            'campaign_id': str(campaign_id),
            'status': campaign.status.value,
            'total_sessions': total_sessions,
            'session_counts': session_counts,
            'success_rate': success_rate,
            'started_at': campaign.started_at.isoformat() if campaign.started_at else None,
            'completed_at': campaign.completed_at.isoformat() if campaign.completed_at else None,
            'queued_jobs': len([job for job in self.job_queue if job.get('campaign_id') == campaign_id])
        }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            'total_jobs': len(self.job_queue),
            'active_workers': len(self.active_workers),
            'max_concurrent_sessions': self.max_concurrent_sessions,
            'available_slots': self.max_concurrent_sessions - len(self.active_workers)
        }
    
    async def add_worker(self, worker_id: str, capacity: int = 1) -> bool:
        """Add a worker to the pool."""
        if worker_id in self.active_workers:
            return False
        
        self.active_workers[worker_id] = {
            'capacity': capacity,
            'current_sessions': 0,
            'last_heartbeat': datetime.utcnow(),
            'status': 'active'
        }
        
        # Process queued jobs
        await self._process_queue()
        
        return True
    
    async def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker from the pool."""
        if worker_id not in self.active_workers:
            return False
        
        # Move active sessions back to queue
        worker = self.active_workers[worker_id]
        for session_id in worker.get('active_sessions', []):
            await self._requeue_session(session_id)
        
        del self.active_workers[worker_id]
        
        return True
    
    async def update_worker_heartbeat(self, worker_id: str) -> bool:
        """Update worker heartbeat."""
        if worker_id not in self.active_workers:
            return False
        
        self.active_workers[worker_id]['last_heartbeat'] = datetime.utcnow()
        return True
    
    async def assign_session_to_worker(self, session_id: UUID, worker_id: str) -> bool:
        """Assign a session to a worker."""
        if worker_id not in self.active_workers:
            return False
        
        worker = self.active_workers[worker_id]
        if worker['current_sessions'] >= worker['capacity']:
            return False
        
        # Update worker
        if 'active_sessions' not in worker:
            worker['active_sessions'] = []
        
        worker['active_sessions'].append(str(session_id))
        worker['current_sessions'] += 1
        
        # Update session status
        await self._update_session_status(session_id, SessionStatus.RUNNING)
        
        return True
    
    async def complete_session(self, session_id: UUID, worker_id: str, success: bool = True) -> bool:
        """Mark a session as completed."""
        if worker_id not in self.active_workers:
            return False
        
        worker = self.active_workers[worker_id]
        if str(session_id) not in worker.get('active_sessions', []):
            return False
        
        # Update worker
        worker['active_sessions'].remove(str(session_id))
        worker['current_sessions'] -= 1
        
        # Update session status
        if success:
            await self._update_session_status(session_id, SessionStatus.COMPLETED)
        else:
            await self._update_session_status(session_id, SessionStatus.FAILED)
        
        # Process more jobs
        await self._process_queue()
        
        return True
    
    async def _get_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID."""
        query = select(Campaign).where(Campaign.id == campaign_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
    
    async def _get_campaign_with_persona(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign with persona."""
        query = (
            select(Campaign)
            .options(selectinload(Campaign.persona))
            .where(Campaign.id == campaign_id)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
    
    async def _get_campaign_with_sessions(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign with sessions."""
        query = (
            select(Campaign)
            .options(selectinload(Campaign.sessions))
            .where(Campaign.id == campaign_id)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
    
    async def _create_campaign_sessions(self, campaign: Campaign) -> None:
        """Create sessions for a campaign."""
        sessions_to_create = []
        
        for i in range(campaign.total_sessions):
            session_data = {
                'campaign_id': str(campaign.id),
                'persona_id': str(campaign.persona_id),
                'start_url': campaign.target_url,
                'user_agent': self._generate_user_agent(campaign.user_agent_rotation),
                'viewport_width': 1920,
                'viewport_height': 1080
            }
            
            sessions_to_create.append(session_data)
        
        # Create sessions in batches
        batch_size = 100
        for i in range(0, len(sessions_to_create), batch_size):
            batch = sessions_to_create[i:i + batch_size]
            await self._create_sessions_batch(batch)
    
    async def _create_sessions_batch(self, sessions_data: List[Dict[str, Any]]) -> None:
        """Create a batch of sessions."""
        sessions = [Session.from_dict(data) for data in sessions_data]
        
        if self.db_session:
            self.db_session.add_all(sessions)
            await self.db_session.commit()
        else:
            async with get_db_session() as session:
                session.add_all(sessions)
                await session.commit()
    
    async def _process_campaign_sessions(self, campaign_id: UUID) -> None:
        """Process sessions for a campaign."""
        # Get pending sessions for the campaign
        query = (
            select(Session)
            .where(
                and_(
                    Session.campaign_id == campaign_id,
                    Session.status == SessionStatus.PENDING
                )
            )
            .limit(self.max_concurrent_sessions)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            sessions = result.scalars().all()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                sessions = result.scalars().all()
        
        # Add sessions to queue
        for session in sessions:
            job = {
                'session_id': str(session.id),
                'campaign_id': str(campaign_id),
                'persona_id': str(session.persona_id),
                'start_url': session.start_url,
                'user_agent': session.user_agent,
                'viewport_width': session.viewport_width,
                'viewport_height': session.viewport_height,
                'created_at': datetime.utcnow().isoformat()
            }
            self.job_queue.append(job)
        
        # Process queue
        await self._process_queue()
    
    async def _process_queue(self) -> None:
        """Process the job queue."""
        available_workers = [
            worker_id for worker_id, worker in self.active_workers.items()
            if worker['current_sessions'] < worker['capacity']
        ]
        
        if not available_workers:
            return
        
        # Assign jobs to available workers
        for worker_id in available_workers:
            if not self.job_queue:
                break
            
            job = self.job_queue.pop(0)
            session_id = UUID(job['session_id'])
            
            if await self.assign_session_to_worker(session_id, worker_id):
                # Send job to worker (in real implementation, this would be a message queue)
                await self._send_job_to_worker(worker_id, job)
    
    async def _requeue_session(self, session_id: UUID) -> None:
        """Requeue a session."""
        # Get session details
        query = select(Session).where(Session.id == session_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            session = result.scalar_one_or_none()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                session = result.scalar_one_or_none()
        
        if not session:
            return
        
        # Add back to queue
        job = {
            'session_id': str(session.id),
            'campaign_id': str(session.campaign_id),
            'persona_id': str(session.persona_id),
            'start_url': session.start_url,
            'user_agent': session.user_agent,
            'viewport_width': session.viewport_width,
            'viewport_height': session.viewport_height,
            'created_at': datetime.utcnow().isoformat()
        }
        self.job_queue.append(job)
    
    async def _update_session_status(self, session_id: UUID, status: SessionStatus) -> None:
        """Update session status."""
        query = (
            update(Session)
            .where(Session.id == session_id)
            .values(status=status)
        )
        
        if self.db_session:
            await self.db_session.execute(query)
            await self.db_session.commit()
        else:
            async with get_db_session() as session:
                await session.execute(query)
                await session.commit()
    
    async def _send_job_to_worker(self, worker_id: str, job: Dict[str, Any]) -> None:
        """Send job to worker (placeholder for message queue integration)."""
        # In a real implementation, this would send a message to a Redis queue
        # or similar message broker
        print(f"Sending job to worker {worker_id}: {job['session_id']}")
    
    def _generate_user_agent(self, rotation_enabled: bool) -> str:
        """Generate user agent string."""
        if not rotation_enabled:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Simple rotation - in real implementation, this would be more sophisticated
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101"
        ]
        
        import random
        return random.choice(user_agents)
