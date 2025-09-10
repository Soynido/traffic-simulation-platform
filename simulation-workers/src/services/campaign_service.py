"""
Service Campaign pour les simulation workers.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import UUID

from ..models.campaign import Campaign


class CampaignService:
    """Service pour la gestion des campagnes."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Récupérer une campagne par son ID."""
        try:
            result = await self.db_session.execute(
                select(Campaign).where(Campaign.id == campaign_id)
            )
            campaign = result.scalar_one_or_none()
            
            if campaign:
                return Campaign(**campaign.__dict__)
            return None
            
        except Exception as e:
            print(f"Erreur lors de la récupération de la campagne {campaign_id}: {e}")
            return None
    
    async def get_all_campaigns(self, limit: int = 100) -> List[Campaign]:
        """Récupérer toutes les campagnes."""
        try:
            result = await self.db_session.execute(
                select(Campaign).limit(limit)
            )
            campaigns = result.scalars().all()
            
            return [Campaign(**campaign.__dict__) for campaign in campaigns]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des campagnes: {e}")
            return []
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[Campaign]:
        """Créer une nouvelle campagne."""
        try:
            campaign = Campaign(**campaign_data)
            
            # Ici, vous devriez insérer en base de données
            # Pour l'instant, on retourne juste l'objet créé
            return campaign
            
        except Exception as e:
            print(f"Erreur lors de la création de la campagne: {e}")
            return None
    
    async def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Optional[Campaign]:
        """Mettre à jour une campagne."""
        try:
            campaign = await self.get_campaign(campaign_id)
            if not campaign:
                return None
            
            # Mettre à jour les champs
            for key, value in campaign_data.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            
            return campaign
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la campagne {campaign_id}: {e}")
            return None
    
    async def delete_campaign(self, campaign_id: str) -> bool:
        """Supprimer une campagne."""
        try:
            # Ici, vous devriez supprimer de la base de données
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression de la campagne {campaign_id}: {e}")
            return False
