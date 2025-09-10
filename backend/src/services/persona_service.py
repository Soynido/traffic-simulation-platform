"""
Service pour la gestion des personas
Implémentation basée sur les tests TDD
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from shared.types import Persona, CreatePersonaRequest, UpdatePersonaRequest
from shared.schemas import validateCreatePersonaRequest, validateUpdatePersonaRequest
from shared.constants import ERROR_CODES

logger = logging.getLogger(__name__)


class PersonaService:
    """Service pour la gestion des personas"""
    
    def __init__(self, db, redis):
        """
        Initialise le service Persona
        
        Args:
            db: Instance de la base de données
            redis: Instance de Redis
        """
        self.db = db
        self.redis = redis
    
    def create_persona(self, create_request: CreatePersonaRequest) -> Persona:
        """
        Crée un nouveau persona
        
        Args:
            create_request: Données de création du persona
            
        Returns:
            Persona créé
            
        Raises:
            ValueError: Si les données sont invalides ou si le nom existe déjà
        """
        try:
            # Validation des données
            validated_data = validateCreatePersonaRequest(create_request)
            
            # Vérification de l'unicité du nom
            existing_persona = self.db.query(Persona).filter(
                Persona.name == validated_data.name
            ).first()
            
            if existing_persona:
                raise ValueError("Persona with this name already exists")
            
            # Création du persona
            persona = Persona(
                id=self._generate_id(),
                name=validated_data.name,
                description=validated_data.description,
                behaviorProfile=validated_data.behaviorProfile,
                demographics=validated_data.demographics,
                technicalProfile=validated_data.technicalProfile,
                isActive=True,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            
            self.db.add(persona)
            self.db.commit()
            self.db.refresh(persona)
            
            logger.info(f"Persona created: {persona.id}")
            return persona
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating persona: {str(e)}")
            raise
    
    def get_persona_by_id(self, persona_id: str) -> Persona:
        """
        Récupère un persona par son ID
        
        Args:
            persona_id: ID du persona
            
        Returns:
            Persona trouvé
            
        Raises:
            ValueError: Si le persona n'existe pas
        """
        try:
            persona = self.db.query(Persona).filter(
                Persona.id == persona_id
            ).first()
            
            if not persona:
                raise ValueError("Persona not found")
            
            return persona
            
        except Exception as e:
            logger.error(f"Error getting persona {persona_id}: {str(e)}")
            raise
    
    def get_personas(
        self, 
        page: int = 1, 
        limit: int = 10, 
        isActive: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Récupère la liste des personas avec pagination
        
        Args:
            page: Numéro de page
            limit: Nombre d'éléments par page
            isActive: Filtrer par statut actif (optionnel)
            
        Returns:
            Dictionnaire contenant les personas et les métadonnées de pagination
        """
        try:
            query = self.db.query(Persona)
            
            # Filtrage par statut actif si spécifié
            if isActive is not None:
                query = query.filter(Persona.isActive == isActive)
            
            # Pagination
            offset = (page - 1) * limit
            personas = query.offset(offset).limit(limit).all()
            
            # Comptage total
            total = query.count()
            
            return {
                "data": personas,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": (total + limit - 1) // limit,
                    "hasNext": page * limit < total,
                    "hasPrevious": page > 1,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting personas: {str(e)}")
            raise
    
    def update_persona(self, persona_id: str, update_data: UpdatePersonaRequest) -> Persona:
        """
        Met à jour un persona
        
        Args:
            persona_id: ID du persona
            update_data: Données de mise à jour
            
        Returns:
            Persona mis à jour
            
        Raises:
            ValueError: Si le persona n'existe pas
        """
        try:
            # Validation des données
            validated_data = validateUpdatePersonaRequest(update_data)
            
            # Récupération du persona
            persona = self.db.query(Persona).filter(
                Persona.id == persona_id
            ).first()
            
            if not persona:
                raise ValueError("Persona not found")
            
            # Mise à jour des champs
            for field, value in validated_data.dict(exclude_unset=True).items():
                setattr(persona, field, value)
            
            persona.updatedAt = datetime.now()
            
            self.db.commit()
            self.db.refresh(persona)
            
            logger.info(f"Persona updated: {persona_id}")
            return persona
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating persona {persona_id}: {str(e)}")
            raise
    
    def delete_persona(self, persona_id: str) -> bool:
        """
        Supprime un persona
        
        Args:
            persona_id: ID du persona
            
        Returns:
            True si supprimé avec succès
            
        Raises:
            ValueError: Si le persona n'existe pas
        """
        try:
            persona = self.db.query(Persona).filter(
                Persona.id == persona_id
            ).first()
            
            if not persona:
                raise ValueError("Persona not found")
            
            self.db.delete(persona)
            self.db.commit()
            
            logger.info(f"Persona deleted: {persona_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting persona {persona_id}: {str(e)}")
            raise
    
    def activate_persona(self, persona_id: str) -> Persona:
        """
        Active un persona
        
        Args:
            persona_id: ID du persona
            
        Returns:
            Persona activé
            
        Raises:
            ValueError: Si le persona n'existe pas
        """
        try:
            persona = self.db.query(Persona).filter(
                Persona.id == persona_id
            ).first()
            
            if not persona:
                raise ValueError("Persona not found")
            
            persona.isActive = True
            persona.updatedAt = datetime.now()
            
            self.db.commit()
            self.db.refresh(persona)
            
            logger.info(f"Persona activated: {persona_id}")
            return persona
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error activating persona {persona_id}: {str(e)}")
            raise
    
    def deactivate_persona(self, persona_id: str) -> Persona:
        """
        Désactive un persona
        
        Args:
            persona_id: ID du persona
            
        Returns:
            Persona désactivé
            
        Raises:
            ValueError: Si le persona n'existe pas
        """
        try:
            persona = self.db.query(Persona).filter(
                Persona.id == persona_id
            ).first()
            
            if not persona:
                raise ValueError("Persona not found")
            
            persona.isActive = False
            persona.updatedAt = datetime.now()
            
            self.db.commit()
            self.db.refresh(persona)
            
            logger.info(f"Persona deactivated: {persona_id}")
            return persona
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating persona {persona_id}: {str(e)}")
            raise
    
    def get_persona_statistics(self) -> Dict[str, int]:
        """
        Récupère les statistiques des personas
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        try:
            total = self.db.query(Persona).count()
            active = self.db.query(Persona).filter(Persona.isActive == True).count()
            inactive = total - active
            
            return {
                "total": total,
                "active": active,
                "inactive": inactive,
            }
            
        except Exception as e:
            logger.error(f"Error getting persona statistics: {str(e)}")
            raise
    
    def _generate_id(self) -> str:
        """
        Génère un ID unique pour un persona
        
        Returns:
            ID unique
        """
        import uuid
        return str(uuid.uuid4())