"""
Persona service (async) compatible avec les endpoints FastAPI.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Persona


class PersonaService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_all_personas(
        self,
        skip: int = 0,
        limit: int = 10,
        name_filter: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> List[Persona]:
        query = select(Persona)
        if name_filter:
            query = query.where(Persona.name.ilike(f"%{name_filter}%"))
        # Basic sort support
        sort_column = getattr(Persona, sort_by, Persona.name)
        query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_persona_count(self) -> int:
        result = await self.db.execute(select(Persona))
        return len(result.scalars().all())

    async def get_persona_by_id(self, persona_id: UUID) -> Optional[Persona]:
        result = await self.db.execute(select(Persona).where(Persona.id == persona_id))
        return result.scalar_one_or_none()

    async def persona_exists(self, persona_id: UUID) -> bool:
        return (await self.get_persona_by_id(persona_id)) is not None

    async def validate_persona_data(self, data: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        min_d = data.get("session_duration_min")
        max_d = data.get("session_duration_max")
        if min_d is not None and max_d is not None and max_d < min_d:
            errors.append("session_duration_max must be >= session_duration_min")
        min_p = data.get("pages_min")
        max_p = data.get("pages_max")
        if min_p is not None and max_p is not None and max_p < min_p:
            errors.append("pages_max must be >= pages_min")
        return errors

    async def create_persona(self, data: Dict[str, Any]) -> Persona:
        persona = Persona.from_dict(data) if hasattr(Persona, 'from_dict') else Persona(**data)
        self.db.add(persona)
        await self.db.commit()
        await self.db.refresh(persona)
        return persona

    async def update_persona(self, persona_id: UUID, data: Dict[str, Any]) -> Optional[Persona]:
        q = (
            update(Persona)
            .where(Persona.id == persona_id)
            .values(**data)
            .returning(Persona)
        )
        result = await self.db.execute(q)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete_persona(self, persona_id: UUID) -> bool:
        result = await self.db.execute(delete(Persona).where(Persona.id == persona_id))
        await self.db.commit()
        # SQLAlchemy 2.0: result.rowcount may be None on some dialects; treat commit success as True
        return True
