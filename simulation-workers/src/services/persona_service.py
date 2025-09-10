"""
Service Persona pour les simulation workers.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import UUID

from ..models.persona import Persona


class PersonaService:
    """Service pour la gestion des personas."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Récupérer une persona par son ID."""
        try:
            result = await self.db_session.execute(
                select(Persona).where(Persona.id == persona_id)
            )
            persona = result.scalar_one_or_none()
            
            if persona:
                return Persona(**persona.__dict__)
            return None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de la persona {persona_id}: {e}")
            return None
    
    async def get_all_personas(self, limit: int = 100) -> List[Persona]:
        """Récupérer toutes les personas."""
        try:
            result = await self.db_session.execute(
                select(Persona).limit(limit)
            )
            personas = result.scalars().all()
            
            return [Persona(**persona.__dict__) for persona in personas]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des personas: {e}")
            return []
    
    async def create_persona(self, persona_data: Dict[str, Any]) -> Optional[Persona]:
        """Créer une nouvelle persona."""
        try:
            persona = Persona(**persona_data)
            
            # Ici, vous devriez insérer en base de données
            # Pour l'instant, on retourne juste l'objet créé
            return persona
            
        except Exception as e:
            print(f"Erreur lors de la création de la persona: {e}")
            return None
    
    async def update_persona(self, persona_id: str, persona_data: Dict[str, Any]) -> Optional[Persona]:
        """Mettre à jour une persona."""
        try:
            persona = await self.get_persona(persona_id)
            if not persona:
                return None
            
            # Mettre à jour les champs
            for key, value in persona_data.items():
                if hasattr(persona, key):
                    setattr(persona, key, value)
            
            return persona
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la persona {persona_id}: {e}")
            return None
    
    async def delete_persona(self, persona_id: str) -> bool:
        """Supprimer une persona."""
        try:
            # Ici, vous devriez supprimer de la base de données
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression de la persona {persona_id}: {e}")
            return False
