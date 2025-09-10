"""
Service Session pour les simulation workers.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import UUID

from ..models.session import Session
from ..models.page_visit import PageVisit
from ..models.action import Action


class SessionService:
    """Service pour la gestion des sessions."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Récupérer une session par son ID."""
        try:
            result = await self.db_session.execute(
                select(Session).where(Session.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if session:
                return Session(**session.__dict__)
            return None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de la session {session_id}: {e}")
            return None
    
    async def get_all_sessions(self, limit: int = 100) -> List[Session]:
        """Récupérer toutes les sessions."""
        try:
            result = await self.db_session.execute(
                select(Session).limit(limit)
            )
            sessions = result.scalars().all()
            
            return [Session(**session.__dict__) for session in sessions]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des sessions: {e}")
            return []
    
    async def create_session(self, session_data: Dict[str, Any]) -> Optional[Session]:
        """Créer une nouvelle session."""
        try:
            session = Session(**session_data)
            
            # Ici, vous devriez insérer en base de données
            # Pour l'instant, on retourne juste l'objet créé
            return session
            
        except Exception as e:
            print(f"Erreur lors de la création de la session: {e}")
            return None
    
    async def update_session_status(self, session_id: str, status: str) -> bool:
        """Mettre à jour le statut d'une session."""
        try:
            # Ici, vous devriez mettre à jour en base de données
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut de la session {session_id}: {e}")
            return False
    
    async def update_session_completion(self, session_id: str, pages_visited: int, actions_performed: int, total_duration: float) -> bool:
        """Mettre à jour les métriques de completion d'une session."""
        try:
            # Ici, vous devriez mettre à jour en base de données
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la completion de la session {session_id}: {e}")
            return False
    
    async def create_page_visit(self, visit_data: Dict[str, Any]) -> Optional[PageVisit]:
        """Créer une visite de page."""
        try:
            visit = PageVisit(**visit_data)
            
            # Ici, vous devriez insérer en base de données
            # Pour l'instant, on retourne juste l'objet créé
            return visit
            
        except Exception as e:
            print(f"Erreur lors de la création de la visite de page: {e}")
            return None
    
    async def create_action(self, action_data: Dict[str, Any]) -> Optional[Action]:
        """Créer une action."""
        try:
            action = Action(**action_data)
            
            # Ici, vous devriez insérer en base de données
            # Pour l'instant, on retourne juste l'objet créé
            return action
            
        except Exception as e:
            print(f"Erreur lors de la création de l'action: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Supprimer une session."""
        try:
            # Ici, vous devriez supprimer de la base de données
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression de la session {session_id}: {e}")
            return False
