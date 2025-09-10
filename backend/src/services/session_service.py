"""
SessionService for managing sessions.
Provides CRUD operations and state management for session entities.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Session, SessionStatus, Campaign, Persona
from ..database.connection import get_db_session


class SessionService:
    """Service for managing session operations."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """Initialize SessionService with optional database session."""
        self.db_session = db_session
    
    async def create_session(self, session_data: Dict[str, Any]) -> Session:
        """Create a new session."""
        session = Session.from_dict(session_data)
        
        if self.db_session:
            self.db_session.add(session)
            await self.db_session.commit()
            await self.db_session.refresh(session)
        else:
            async with get_db_session() as db_session:
                db_session.add(session)
                await db_session.commit()
                await db_session.refresh(session)
        
        return session
    
    async def get_session_by_id(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        query = (
            select(Session)
            .options(
                selectinload(Session.campaign),
                selectinload(Session.persona),
                selectinload(Session.page_visits)
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
    
    async def get_sessions_by_campaign(
        self, 
        campaign_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[SessionStatus] = None
    ) -> List[Session]:
        """Get sessions by campaign ID."""
        query = (
            select(Session)
            .options(selectinload(Session.persona))
            .where(Session.campaign_id == campaign_id)
        )
        
        if status_filter:
            query = query.where(Session.status == status_filter)
        
        query = query.order_by(Session.created_at.desc()).offset(skip).limit(limit)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalars().all()
    
    async def get_sessions_by_persona(
        self,
        persona_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Session]:
        """Get sessions by persona ID."""
        query = (
            select(Session)
            .options(selectinload(Session.campaign))
            .where(Session.persona_id == persona_id)
            .order_by(Session.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalars().all()
    
    async def get_all_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[SessionStatus] = None,
        campaign_id_filter: Optional[UUID] = None
    ) -> List[Session]:
        """Get all sessions with optional filtering."""
        query = (
            select(Session)
            .options(
                selectinload(Session.campaign),
                selectinload(Session.persona)
            )
        )
        
        if status_filter:
            query = query.where(Session.status == status_filter)
        
        if campaign_id_filter:
            query = query.where(Session.campaign_id == campaign_id_filter)
        
        query = query.order_by(Session.created_at.desc()).offset(skip).limit(limit)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalars().all()
    
    async def update_session(self, session_id: UUID, update_data: Dict[str, Any]) -> Optional[Session]:
        """Update session by ID."""
        # Remove id from update_data if present
        update_data.pop('id', None)
        
        query = (
            update(Session)
            .where(Session.id == session_id)
            .values(**update_data)
            .returning(Session)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                await db_session.commit()
                return result.scalar_one_or_none()
    
    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session by ID."""
        query = delete(Session).where(Session.id == session_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            return result.rowcount > 0
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                await db_session.commit()
                return result.rowcount > 0
    
    async def start_session(self, session_id: UUID) -> Optional[Session]:
        """Start a session."""
        session = await self.get_session_by_id(session_id)
        if not session:
            return None
        
        try:
            session.start()
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(session)
            else:
                async with get_db_session() as db_session:
                    db_session.add(session)
                    await db_session.commit()
                    await db_session.refresh(session)
            
            return session
        except ValueError as e:
            raise ValueError(f"Cannot start session: {str(e)}")
    
    async def complete_session(self, session_id: UUID, duration_ms: Optional[int] = None) -> Optional[Session]:
        """Complete a session."""
        session = await self.get_session_by_id(session_id)
        if not session:
            return None
        
        try:
            session.complete(duration_ms)
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(session)
            else:
                async with get_db_session() as db_session:
                    db_session.add(session)
                    await db_session.commit()
                    await db_session.refresh(session)
            
            return session
        except ValueError as e:
            raise ValueError(f"Cannot complete session: {str(e)}")
    
    async def fail_session(self, session_id: UUID, error_message: Optional[str] = None) -> Optional[Session]:
        """Mark session as failed."""
        session = await self.get_session_by_id(session_id)
        if not session:
            return None
        
        try:
            session.fail(error_message)
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(session)
            else:
                async with get_db_session() as db_session:
                    db_session.add(session)
                    await db_session.commit()
                    await db_session.refresh(session)
            
            return session
        except ValueError as e:
            raise ValueError(f"Cannot fail session: {str(e)}")
    
    async def timeout_session(self, session_id: UUID) -> Optional[Session]:
        """Mark session as timed out."""
        session = await self.get_session_by_id(session_id)
        if not session:
            return None
        
        try:
            session.timeout()
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(session)
            else:
                async with get_db_session() as db_session:
                    db_session.add(session)
                    await db_session.commit()
                    await db_session.refresh(session)
            
            return session
        except ValueError as e:
            raise ValueError(f"Cannot timeout session: {str(e)}")
    
    async def update_session_metrics(
        self, 
        session_id: UUID, 
        pages_visited: Optional[int] = None,
        total_actions: Optional[int] = None
    ) -> Optional[Session]:
        """Update session metrics."""
        update_data = {}
        
        if pages_visited is not None:
            update_data['pages_visited'] = pages_visited
        
        if total_actions is not None:
            update_data['total_actions'] = total_actions
        
        if not update_data:
            return await self.get_session_by_id(session_id)
        
        return await self.update_session(session_id, update_data)
    
    async def session_exists(self, session_id: UUID) -> bool:
        """Check if session exists."""
        session = await self.get_session_by_id(session_id)
        return session is not None
    
    async def get_session_count(
        self, 
        campaign_id: Optional[UUID] = None,
        status_filter: Optional[SessionStatus] = None
    ) -> int:
        """Get total count of sessions."""
        query = select(Session.id)
        
        if campaign_id:
            query = query.where(Session.campaign_id == campaign_id)
        
        if status_filter:
            query = query.where(Session.status == status_filter)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return len(result.scalars().all())
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return len(result.scalars().all())
    
    async def get_sessions_by_status(self, status: SessionStatus) -> List[Session]:
        """Get sessions by status."""
        query = (
            select(Session)
            .options(
                selectinload(Session.campaign),
                selectinload(Session.persona)
            )
            .where(Session.status == status)
            .order_by(Session.created_at.desc())
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                return result.scalars().all()
    
    async def validate_session_data(self, session_data: Dict[str, Any]) -> List[str]:
        """Validate session data and return list of errors."""
        errors = []
        
        # Required fields
        required_fields = ['campaign_id', 'persona_id', 'start_url', 'user_agent']
        for field in required_fields:
            if field not in session_data or session_data[field] is None:
                errors.append(f"Field '{field}' is required")
        
        if errors:
            return errors
        
        # Validate UUIDs
        try:
            campaign_id = UUID(str(session_data['campaign_id']))
            persona_id = UUID(str(session_data['persona_id']))
        except ValueError:
            errors.append("campaign_id and persona_id must be valid UUIDs")
            return errors
        
        # Validate campaign exists
        query = select(Campaign).where(Campaign.id == campaign_id)
        if self.db_session:
            result = await self.db_session.execute(query)
            if not result.scalar_one_or_none():
                errors.append("campaign_id does not exist")
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                if not result.scalar_one_or_none():
                    errors.append("campaign_id does not exist")
        
        # Validate persona exists
        query = select(Persona).where(Persona.id == persona_id)
        if self.db_session:
            result = await self.db_session.execute(query)
            if not result.scalar_one_or_none():
                errors.append("persona_id does not exist")
        else:
            async with get_db_session() as db_session:
                result = await db_session.execute(query)
                if not result.scalar_one_or_none():
                    errors.append("persona_id does not exist")
        
        # Validate URL format
        start_url = session_data.get('start_url', '')
        if not start_url.startswith(('http://', 'https://')):
            errors.append("start_url must be a valid HTTP/HTTPS URL")
        
        # Validate viewport dimensions
        viewport_width = session_data.get('viewport_width', 1920)
        viewport_height = session_data.get('viewport_height', 1080)
        
        if viewport_width <= 0 or viewport_height <= 0:
            errors.append("viewport dimensions must be positive")
        
        return errors
