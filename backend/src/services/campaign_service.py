"""
CampaignService for managing campaigns.
Provides CRUD operations and state management for campaign entities.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Campaign, CampaignStatus, Persona
from ..database.connection import get_db_session


class CampaignService:
    """Service for managing campaign operations."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """Initialize CampaignService with optional database session."""
        self.db_session = db_session
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Campaign:
        """Create a new campaign."""
        campaign = Campaign.from_dict(campaign_data)
        
        if self.db_session:
            self.db_session.add(campaign)
            await self.db_session.commit()
            await self.db_session.refresh(campaign)
        else:
            async with get_db_session() as session:
                session.add(campaign)
                await session.commit()
                await session.refresh(campaign)
        
        return campaign
    
    async def get_campaign_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID."""
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
    
    async def get_all_campaigns(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[CampaignStatus] = None,
        persona_id_filter: Optional[UUID] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> List[Campaign]:
        """Get all campaigns with optional filtering and sorting."""
        query = select(Campaign).options(selectinload(Campaign.persona))
        
        # Apply filters
        if status_filter:
            query = query.where(Campaign.status == status_filter)
        
        if persona_id_filter:
            query = query.where(Campaign.persona_id == persona_id_filter)
        
        # Apply sorting
        if hasattr(Campaign, sort_by):
            sort_column = getattr(Campaign, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalars().all()
    
    async def update_campaign(self, campaign_id: UUID, update_data: Dict[str, Any]) -> Optional[Campaign]:
        """Update campaign by ID."""
        # Remove id from update_data if present
        update_data.pop('id', None)
        
        query = (
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(**update_data)
            .returning(Campaign)
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one_or_none()
    
    async def delete_campaign(self, campaign_id: UUID) -> bool:
        """Delete campaign by ID."""
        query = delete(Campaign).where(Campaign.id == campaign_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            return result.rowcount > 0
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                await session.commit()
                return result.rowcount > 0
    
    async def start_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Start a campaign."""
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
        
        try:
            campaign.start()
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(campaign)
            else:
                async with get_db_session() as session:
                    session.add(campaign)
                    await session.commit()
                    await session.refresh(campaign)
            
            return campaign
        except ValueError as e:
            raise ValueError(f"Cannot start campaign: {str(e)}")
    
    async def pause_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Pause a campaign."""
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
        
        try:
            campaign.pause()
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(campaign)
            else:
                async with get_db_session() as session:
                    session.add(campaign)
                    await session.commit()
                    await session.refresh(campaign)
            
            return campaign
        except ValueError as e:
            raise ValueError(f"Cannot pause campaign: {str(e)}")
    
    async def resume_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Resume a campaign."""
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
        
        try:
            campaign.resume()
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(campaign)
            else:
                async with get_db_session() as session:
                    session.add(campaign)
                    await session.commit()
                    await session.refresh(campaign)
            
            return campaign
        except ValueError as e:
            raise ValueError(f"Cannot resume campaign: {str(e)}")
    
    async def stop_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Stop a campaign."""
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
        
        try:
            campaign.stop()
            
            if self.db_session:
                await self.db_session.commit()
                await self.db_session.refresh(campaign)
            else:
                async with get_db_session() as session:
                    session.add(campaign)
                    await session.commit()
                    await session.refresh(campaign)
            
            return campaign
        except ValueError as e:
            raise ValueError(f"Cannot stop campaign: {str(e)}")
    
    async def complete_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Mark campaign as completed."""
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
        
        campaign.complete()
        
        if self.db_session:
            await self.db_session.commit()
            await self.db_session.refresh(campaign)
        else:
            async with get_db_session() as session:
                session.add(campaign)
                await session.commit()
                await session.refresh(campaign)
        
        return campaign
    
    async def fail_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Mark campaign as failed."""
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
        
        campaign.fail()
        
        if self.db_session:
            await self.db_session.commit()
            await self.db_session.refresh(campaign)
        else:
            async with get_db_session() as session:
                session.add(campaign)
                await session.commit()
                await session.refresh(campaign)
        
        return campaign
    
    async def campaign_exists(self, campaign_id: UUID) -> bool:
        """Check if campaign exists."""
        campaign = await self.get_campaign_by_id(campaign_id)
        return campaign is not None
    
    async def get_campaigns_by_status(self, status: CampaignStatus) -> List[Campaign]:
        """Get campaigns by status."""
        query = (
            select(Campaign)
            .options(selectinload(Campaign.persona))
            .where(Campaign.status == status)
            .order_by(Campaign.created_at.desc())
        )
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalars().all()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalars().all()
    
    async def get_campaign_count(self, status_filter: Optional[CampaignStatus] = None) -> int:
        """Get total count of campaigns."""
        query = select(Campaign.id)
        
        if status_filter:
            query = query.where(Campaign.status == status_filter)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return len(result.scalars().all())
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return len(result.scalars().all())
    
    async def validate_campaign_data(self, campaign_data: Dict[str, Any]) -> List[str]:
        """Validate campaign data and return list of errors."""
        errors = []
        
        # Required fields
        required_fields = ['name', 'target_url', 'total_sessions', 'persona_id']
        for field in required_fields:
            if field not in campaign_data or campaign_data[field] is None:
                errors.append(f"Field '{field}' is required")
        
        if errors:
            return errors
        
        # Validate numeric ranges
        if campaign_data.get('total_sessions', 0) <= 0:
            errors.append("total_sessions must be positive")
        
        concurrent_sessions = campaign_data.get('concurrent_sessions', 10)
        if concurrent_sessions <= 0:
            errors.append("concurrent_sessions must be positive")
        
        if concurrent_sessions > campaign_data.get('total_sessions', 0):
            errors.append("concurrent_sessions must be <= total_sessions")
        
        # Validate rate limit delay
        rate_limit = campaign_data.get('rate_limit_delay_ms', 1000)
        if rate_limit < 100:
            errors.append("rate_limit_delay_ms must be >= 100")
        
        # Validate URL format (basic check)
        target_url = campaign_data.get('target_url', '')
        if not str(target_url).startswith(('http://', 'https://')):
            errors.append("target_url must be a valid HTTP/HTTPS URL")
        
        # Validate persona exists
        persona_id = campaign_data.get('persona_id')
        if persona_id:
            try:
                persona_uuid = UUID(str(persona_id))
                # Check if persona exists (simplified - in real app, inject PersonaService)
                query = select(Persona).where(Persona.id == persona_uuid)
                if self.db_session:
                    result = await self.db_session.execute(query)
                    if not result.scalar_one_or_none():
                        errors.append("persona_id does not exist")
                else:
                    async with get_db_session() as session:
                        result = await session.execute(query)
                        if not result.scalar_one_or_none():
                            errors.append("persona_id does not exist")
            except ValueError:
                errors.append("persona_id must be a valid UUID")
        
        return errors
