"""
PersonaService for managing personas.
Provides CRUD operations for persona entities.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Persona
from ..database.connection import get_db_session


class PersonaService:
    """Service for managing persona operations."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """Initialize PersonaService with optional database session."""
        self.db_session = db_session
    
    async def create_persona(self, persona_data: Dict[str, Any]) -> Persona:
        """Create a new persona."""
        persona = Persona.from_dict(persona_data)
        
        if self.db_session:
            self.db_session.add(persona)
            await self.db_session.commit()
            await self.db_session.refresh(persona)
        else:
            async with get_db_session() as session:
                session.add(persona)
                await session.commit()
                await session.refresh(persona)
        
        return persona
    
    async def get_persona_by_id(self, persona_id: UUID) -> Optional[Persona]:
        """Get persona by ID."""
        query = select(Persona).where(Persona.id == persona_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
    
    async def get_persona_by_name(self, name: str) -> Optional[Persona]:
        """Get persona by name."""
        query = select(Persona).where(Persona.name == name)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()
    
    async def get_all_personas(
        self, 
        skip: int = 0, 
        limit: int = 100,
        name_filter: Optional[str] = None,
        sort_by: str = 'name',
        sort_order: str = 'asc'
    ) -> List[Persona]:
        """Get all personas with optional filtering and sorting."""
        query = select(Persona)
        
        # Apply name filter
        if name_filter:
            query = query.where(Persona.name.ilike(f'%{name_filter}%'))
        
        # Apply sorting
        if hasattr(Persona, sort_by):
            sort_column = getattr(Persona, sort_by)
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
    
    async def update_persona(self, persona_id: UUID, update_data: Dict[str, Any]) -> Optional[Persona]:
        """Update persona by ID."""
        # Remove id from update_data if present
        update_data.pop('id', None)
        
        query = (
            update(Persona)
            .where(Persona.id == persona_id)
            .values(**update_data)
            .returning(Persona)
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
    
    async def delete_persona(self, persona_id: UUID) -> bool:
        """Delete persona by ID."""
        query = delete(Persona).where(Persona.id == persona_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            return result.rowcount > 0
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                await session.commit()
                return result.rowcount > 0
    
    async def persona_exists(self, persona_id: UUID) -> bool:
        """Check if persona exists."""
        persona = await self.get_persona_by_id(persona_id)
        return persona is not None
    
    async def name_exists(self, name: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if persona name exists (excluding specific ID)."""
        query = select(Persona).where(Persona.name == name)
        
        if exclude_id:
            query = query.where(Persona.id != exclude_id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none() is not None
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none() is not None
    
    async def get_persona_count(self) -> int:
        """Get total count of personas."""
        query = select(Persona.id)
        
        if self.db_session:
            result = await self.db_session.execute(query)
            return len(result.scalars().all())
        else:
            async with get_db_session() as session:
                result = await session.execute(query)
                return len(result.scalars().all())
    
    async def validate_persona_data(self, persona_data: Dict[str, Any]) -> List[str]:
        """Validate persona data and return list of errors."""
        errors = []
        
        # Required fields
        required_fields = ['name', 'session_duration_min', 'session_duration_max', 'pages_min', 'pages_max']
        for field in required_fields:
            if field not in persona_data or persona_data[field] is None:
                errors.append(f"Field '{field}' is required")
        
        if errors:
            return errors
        
        # Validate numeric ranges
        if persona_data.get('session_duration_min', 0) <= 0:
            errors.append("session_duration_min must be positive")
        
        if persona_data.get('session_duration_max', 0) < persona_data.get('session_duration_min', 0):
            errors.append("session_duration_max must be >= session_duration_min")
        
        if persona_data.get('pages_min', 0) <= 0:
            errors.append("pages_min must be positive")
        
        if persona_data.get('pages_max', 0) < persona_data.get('pages_min', 0):
            errors.append("pages_max must be >= pages_min")
        
        # Validate probabilities
        probability_fields = ['scroll_probability', 'click_probability', 'typing_probability']
        for field in probability_fields:
            value = persona_data.get(field, 0.0)
            if not (0.0 <= value <= 1.0):
                errors.append(f"{field} must be between 0.0 and 1.0")
        
        # Validate name uniqueness
        name = persona_data.get('name')
        if name:
            exclude_id = persona_data.get('id')
            if await self.name_exists(name, exclude_id):
                errors.append("Persona name already exists")
        
        return errors
