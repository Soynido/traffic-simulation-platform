"""
Tests unitaires pour le service Persona
Approche TDD : Tests d'abord, implémentation ensuite
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import List

# Import des types partagés (à implémenter)
from shared.types import Persona, CreatePersonaRequest, UpdatePersonaRequest
from shared.constants import ERROR_CODES
from shared.schemas import validateCreatePersonaRequest, validateUpdatePersonaRequest

# Import du service à implémenter
from services.persona_service import PersonaService


class TestPersonaService:
    """Tests pour le service Persona"""
    
    @pytest.fixture
    def persona_service(self):
        """Fixture pour créer une instance du service Persona"""
        mock_db = Mock()
        mock_redis = Mock()
        return PersonaService(db=mock_db, redis=mock_redis)
    
    @pytest.fixture
    def sample_persona_data(self):
        """Données d'exemple pour un persona"""
        return {
            "name": "Test Persona",
            "description": "A test persona for unit testing",
            "behaviorProfile": {
                "browsingSpeed": "normal",
                "clickPattern": "systematic",
                "scrollBehavior": "smooth",
                "sessionDuration": {"min": 5, "max": 30},
                "pageViewsPerSession": {"min": 3, "max": 10},
                "timeOnPage": {"min": 10, "max": 120},
            },
            "demographics": {
                "age": {"min": 25, "max": 45},
                "gender": "prefer_not_to_say",
                "location": {"country": "US"},
                "interests": ["technology"],
            },
            "technicalProfile": {
                "deviceTypes": [{"type": "desktop", "probability": 1.0}],
                "browsers": [{"name": "Chrome", "version": "120", "userAgent": "", "probability": 1.0}],
                "operatingSystems": [{"name": "Windows", "version": "10", "probability": 1.0}],
                "screenResolutions": [{"width": 1920, "height": 1080, "probability": 1.0}],
                "connectionTypes": [{"type": "wifi", "speed": "fast", "probability": 1.0}],
                "timezone": "UTC",
            },
        }
    
    @pytest.fixture
    def sample_persona(self, sample_persona_data):
        """Persona d'exemple complet"""
        return Persona(
            id="123e4567-e89b-12d3-a456-426614174000",
            name=sample_persona_data["name"],
            description=sample_persona_data["description"],
            behaviorProfile=sample_persona_data["behaviorProfile"],
            demographics=sample_persona_data["demographics"],
            technicalProfile=sample_persona_data["technicalProfile"],
            isActive=True,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )

    def test_create_persona_success(self, persona_service, sample_persona_data):
        """Test: Créer un persona avec succès"""
        # Arrange
        create_request = CreatePersonaRequest(**sample_persona_data)
        expected_persona = Persona(
            id="123e4567-e89b-12d3-a456-426614174000",
            name=create_request.name,
            description=create_request.description,
            behaviorProfile=create_request.behaviorProfile,
            demographics=create_request.demographics,
            technicalProfile=create_request.technicalProfile,
            isActive=True,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        
        persona_service.db.query.return_value.filter.return_value.first.return_value = None
        persona_service.db.add.return_value = None
        persona_service.db.commit.return_value = None
        persona_service.db.refresh.return_value = None
        
        # Act
        result = persona_service.create_persona(create_request)
        
        # Assert
        assert result is not None
        assert result.name == create_request.name
        assert result.description == create_request.description
        assert result.isActive is True
        persona_service.db.add.assert_called_once()
        persona_service.db.commit.assert_called_once()

    def test_create_persona_validation_error(self, persona_service):
        """Test: Créer un persona avec des données invalides"""
        # Arrange
        invalid_data = {
            "name": "",  # Nom vide - invalide
            "description": "A test persona",
            "behaviorProfile": {},
            "demographics": {},
            "technicalProfile": {},
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation error"):
            create_request = CreatePersonaRequest(**invalid_data)
            persona_service.create_persona(create_request)

    def test_create_persona_duplicate_name(self, persona_service, sample_persona_data):
        """Test: Créer un persona avec un nom déjà existant"""
        # Arrange
        create_request = CreatePersonaRequest(**sample_persona_data)
        existing_persona = Persona(
            id="existing-id",
            name=create_request.name,
            description="Existing persona",
            behaviorProfile=create_request.behaviorProfile,
            demographics=create_request.demographics,
            technicalProfile=create_request.technicalProfile,
            isActive=True,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        
        persona_service.db.query.return_value.filter.return_value.first.return_value = existing_persona
        
        # Act & Assert
        with pytest.raises(ValueError, match="Persona with this name already exists"):
            persona_service.create_persona(create_request)

    def test_get_persona_by_id_success(self, persona_service, sample_persona):
        """Test: Récupérer un persona par ID avec succès"""
        # Arrange
        persona_id = sample_persona.id
        persona_service.db.query.return_value.filter.return_value.first.return_value = sample_persona
        
        # Act
        result = persona_service.get_persona_by_id(persona_id)
        
        # Assert
        assert result is not None
        assert result.id == persona_id
        assert result.name == sample_persona.name

    def test_get_persona_by_id_not_found(self, persona_service):
        """Test: Récupérer un persona inexistant"""
        # Arrange
        persona_id = "non-existent-id"
        persona_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Persona not found"):
            persona_service.get_persona_by_id(persona_id)

    def test_get_personas_success(self, persona_service, sample_persona):
        """Test: Récupérer la liste des personas avec succès"""
        # Arrange
        personas = [sample_persona]
        persona_service.db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = personas
        persona_service.db.query.return_value.count.return_value = 1
        
        # Act
        result = persona_service.get_personas(page=1, limit=10, isActive=None)
        
        # Assert
        assert result is not None
        assert len(result["data"]) == 1
        assert result["data"][0].id == sample_persona.id
        assert result["pagination"]["total"] == 1

    def test_get_personas_with_filters(self, persona_service, sample_persona):
        """Test: Récupérer les personas avec des filtres"""
        # Arrange
        personas = [sample_persona]
        persona_service.db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = personas
        persona_service.db.query.return_value.count.return_value = 1
        
        # Act
        result = persona_service.get_personas(page=1, limit=10, isActive=True)
        
        # Assert
        assert result is not None
        assert len(result["data"]) == 1

    def test_update_persona_success(self, persona_service, sample_persona):
        """Test: Mettre à jour un persona avec succès"""
        # Arrange
        persona_id = sample_persona.id
        update_data = UpdatePersonaRequest(name="Updated Name")
        
        persona_service.db.query.return_value.filter.return_value.first.return_value = sample_persona
        persona_service.db.commit.return_value = None
        persona_service.db.refresh.return_value = None
        
        # Act
        result = persona_service.update_persona(persona_id, update_data)
        
        # Assert
        assert result is not None
        assert result.name == "Updated Name"
        persona_service.db.commit.assert_called_once()

    def test_update_persona_not_found(self, persona_service):
        """Test: Mettre à jour un persona inexistant"""
        # Arrange
        persona_id = "non-existent-id"
        update_data = UpdatePersonaRequest(name="Updated Name")
        
        persona_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Persona not found"):
            persona_service.update_persona(persona_id, update_data)

    def test_delete_persona_success(self, persona_service, sample_persona):
        """Test: Supprimer un persona avec succès"""
        # Arrange
        persona_id = sample_persona.id
        persona_service.db.query.return_value.filter.return_value.first.return_value = sample_persona
        persona_service.db.delete.return_value = None
        persona_service.db.commit.return_value = None
        
        # Act
        result = persona_service.delete_persona(persona_id)
        
        # Assert
        assert result is True
        persona_service.db.delete.assert_called_once_with(sample_persona)
        persona_service.db.commit.assert_called_once()

    def test_delete_persona_not_found(self, persona_service):
        """Test: Supprimer un persona inexistant"""
        # Arrange
        persona_id = "non-existent-id"
        persona_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Persona not found"):
            persona_service.delete_persona(persona_id)

    def test_activate_persona_success(self, persona_service, sample_persona):
        """Test: Activer un persona avec succès"""
        # Arrange
        persona_id = sample_persona.id
        sample_persona.isActive = False
        persona_service.db.query.return_value.filter.return_value.first.return_value = sample_persona
        persona_service.db.commit.return_value = None
        
        # Act
        result = persona_service.activate_persona(persona_id)
        
        # Assert
        assert result is not None
        assert result.isActive is True
        persona_service.db.commit.assert_called_once()

    def test_deactivate_persona_success(self, persona_service, sample_persona):
        """Test: Désactiver un persona avec succès"""
        # Arrange
        persona_id = sample_persona.id
        sample_persona.isActive = True
        persona_service.db.query.return_value.filter.return_value.first.return_value = sample_persona
        persona_service.db.commit.return_value = None
        
        # Act
        result = persona_service.deactivate_persona(persona_id)
        
        # Assert
        assert result is not None
        assert result.isActive is False
        persona_service.db.commit.assert_called_once()

    def test_get_persona_statistics(self, persona_service, sample_persona):
        """Test: Récupérer les statistiques des personas"""
        # Arrange
        personas = [sample_persona]
        persona_service.db.query.return_value.all.return_value = personas
        
        # Act
        result = persona_service.get_persona_statistics()
        
        # Assert
        assert result is not None
        assert "total" in result
        assert "active" in result
        assert "inactive" in result
        assert result["total"] == 1

    @patch('services.persona_service.validateCreatePersonaRequest')
    def test_create_persona_validation_called(self, mock_validate, persona_service, sample_persona_data):
        """Test: Vérifier que la validation est appelée lors de la création"""
        # Arrange
        create_request = CreatePersonaRequest(**sample_persona_data)
        mock_validate.return_value = create_request
        persona_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        persona_service.create_persona(create_request)
        
        # Assert
        mock_validate.assert_called_once_with(create_request)

    @patch('services.persona_service.validateUpdatePersonaRequest')
    def test_update_persona_validation_called(self, mock_validate, persona_service, sample_persona):
        """Test: Vérifier que la validation est appelée lors de la mise à jour"""
        # Arrange
        persona_id = sample_persona.id
        update_data = UpdatePersonaRequest(name="Updated Name")
        mock_validate.return_value = update_data
        persona_service.db.query.return_value.filter.return_value.first.return_value = sample_persona
        
        # Act
        persona_service.update_persona(persona_id, update_data)
        
        # Assert
        mock_validate.assert_called_once_with(update_data)

    def test_persona_service_initialization(self):
        """Test: Vérifier l'initialisation du service"""
        # Arrange
        mock_db = Mock()
        mock_redis = Mock()
        
        # Act
        service = PersonaService(db=mock_db, redis=mock_redis)
        
        # Assert
        assert service.db == mock_db
        assert service.redis == mock_redis

    def test_persona_service_error_handling(self, persona_service):
        """Test: Vérifier la gestion d'erreur du service"""
        # Arrange
        persona_service.db.query.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            persona_service.get_personas()
