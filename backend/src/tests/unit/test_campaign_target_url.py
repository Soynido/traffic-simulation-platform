"""
Tests unitaires pour le champ target_url dans les campagnes
Approche TDD : Tests d'abord, implémentation ensuite
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from pydantic import ValidationError

# Import des types partagés
from shared.types import Campaign, CreateCampaignRequest
from shared.schemas import validateCreateCampaignRequest

# Import du service à implémenter
from services.campaign_service import CampaignService


class TestCampaignTargetUrl:
    """Tests pour le champ target_url dans les campagnes"""
    
    @pytest.fixture
    def campaign_service(self):
        """Fixture pour créer une instance du service Campaign"""
        mock_db = Mock()
        mock_redis = Mock()
        return CampaignService(db=mock_db, redis=mock_redis)
    
    @pytest.fixture
    def sample_campaign_data_with_url(self):
        """Données d'exemple pour une campagne avec target_url"""
        return {
            "name": "Test Real Visits",
            "description": "Campaign to test real website visits",
            "target_url": "https://example.com",
            "total_sessions": 10,
            "concurrent_sessions": 10,
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "rate_limit_delay_ms": 1000,
            "user_agent_rotation": True,
            "respect_robots_txt": True,
        }

    def test_create_campaign_with_valid_target_url(self, campaign_service, sample_campaign_data_with_url):
        """Test: Créer une campagne avec une URL cible valide"""
        # Arrange
        create_request = CreateCampaignRequest(**sample_campaign_data_with_url)
        expected_campaign = Campaign(
            id="123e4567-e89b-12d3-a456-426614174000",
            name=create_request.name,
            description=create_request.description,
            target_url=create_request.target_url,
            personaIds=create_request.personaIds,
            simulationConfig=create_request.simulationConfig,
            status="draft",
            metrics={
                "totalSessions": 0,
                "completedSessions": 0,
                "failedSessions": 0,
                "averageSessionDuration": 0,
                "totalPageViews": 0,
                "uniquePageViews": 0,
                "bounceRate": 0,
                "conversionRate": 0,
            },
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        
        campaign_service.db.query.return_value.filter.return_value.first.return_value = None
        campaign_service.db.add.return_value = None
        campaign_service.db.commit.return_value = None
        campaign_service.db.refresh.return_value = None
        
        # Act
        result = campaign_service.create_campaign(create_request)
        
        # Assert
        assert result is not None
        assert result.target_url == "https://example.com"
        assert result.name == "Test Real Visits"
        campaign_service.db.add.assert_called_once()
        campaign_service.db.commit.assert_called_once()

    def test_create_campaign_with_invalid_target_url(self, campaign_service):
        """Test: Créer une campagne avec une URL cible invalide"""
        # Arrange
        invalid_data = {
            "name": "Test Campaign",
            "description": "Test description",
            "target_url": "not-a-valid-url",  # URL invalide
            "total_sessions": 5,
            "concurrent_sessions": 5,
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "rate_limit_delay_ms": 1000,
            "user_agent_rotation": True,
            "respect_robots_txt": True,
        }
        
        # Act & Assert
        with pytest.raises(ValidationError):
            create_request = CreateCampaignRequest(**invalid_data)
            campaign_service.create_campaign(create_request)

    def test_create_campaign_with_http_url(self, campaign_service):
        """Test: Créer une campagne avec une URL HTTP (non-HTTPS)"""
        # Arrange
        http_data = {
            "name": "Test HTTP Campaign",
            "description": "Test with HTTP URL",
            "target_url": "http://example.com",  # HTTP au lieu de HTTPS
            "total_sessions": 5,
            "concurrent_sessions": 5,
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "rate_limit_delay_ms": 1000,
            "user_agent_rotation": True,
            "respect_robots_txt": True,
        }
        
        create_request = CreateCampaignRequest(**http_data)
        campaign_service.db.query.return_value.filter.return_value.first.return_value = None
        campaign_service.db.add.return_value = None
        campaign_service.db.commit.return_value = None
        campaign_service.db.refresh.return_value = None
        
        # Act
        result = campaign_service.create_campaign(create_request)
        
        # Assert
        assert result is not None
        assert result.target_url == "http://example.com"

    def test_create_campaign_with_localhost_url(self, campaign_service):
        """Test: Créer une campagne avec une URL localhost"""
        # Arrange
        localhost_data = {
            "name": "Test Localhost Campaign",
            "description": "Test with localhost URL",
            "target_url": "http://localhost:3000",
            "total_sessions": 5,
            "concurrent_sessions": 5,
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "rate_limit_delay_ms": 1000,
            "user_agent_rotation": True,
            "respect_robots_txt": True,
        }
        
        create_request = CreateCampaignRequest(**localhost_data)
        campaign_service.db.query.return_value.filter.return_value.first.return_value = None
        campaign_service.db.add.return_value = None
        campaign_service.db.commit.return_value = None
        campaign_service.db.refresh.return_value = None
        
        # Act
        result = campaign_service.create_campaign(create_request)
        
        # Assert
        assert result is not None
        assert result.target_url == "http://localhost:3000"

    def test_create_campaign_without_target_url(self, campaign_service):
        """Test: Créer une campagne sans target_url (devrait échouer)"""
        # Arrange
        data_without_url = {
            "name": "Test Campaign",
            "description": "Test description",
            "total_sessions": 5,
            "concurrent_sessions": 5,
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "rate_limit_delay_ms": 1000,
            "user_agent_rotation": True,
            "respect_robots_txt": True,
        }
        
        # Act & Assert
        with pytest.raises(ValidationError):
            create_request = CreateCampaignRequest(**data_without_url)
            campaign_service.create_campaign(create_request)

    def test_update_campaign_target_url(self, campaign_service):
        """Test: Mettre à jour l'URL cible d'une campagne existante"""
        # Arrange
        campaign_id = "123e4567-e89b-12d3-a456-426614174000"
        existing_campaign = Campaign(
            id=campaign_id,
            name="Existing Campaign",
            description="Existing description",
            target_url="https://old-example.com",
            personaIds=["123e4567-e89b-12d3-a456-426614174001"],
            simulationConfig={
                "concurrentSessions": 5,
                "sessionInterval": 30,
                "duration": 60,
                "randomization": {
                    "enabled": True,
                    "timeVariation": 0.1,
                    "actionVariation": 0.1,
                    "pathVariation": 0.1,
                },
                "behaviorVariation": 0.1,
            },
            status="draft",
            metrics={
                "totalSessions": 0,
                "completedSessions": 0,
                "failedSessions": 0,
                "averageSessionDuration": 0,
                "totalPageViews": 0,
                "uniquePageViews": 0,
                "bounceRate": 0,
                "conversionRate": 0,
            },
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        
        update_data = {"target_url": "https://new-example.com"}
        
        campaign_service.db.query.return_value.filter.return_value.first.return_value = existing_campaign
        campaign_service.db.commit.return_value = None
        campaign_service.db.refresh.return_value = None
        
        # Act
        result = campaign_service.update_campaign(campaign_id, update_data)
        
        # Assert
        assert result is not None
        assert result.target_url == "https://new-example.com"
        campaign_service.db.commit.assert_called_once()

    def test_get_campaign_with_target_url(self, campaign_service):
        """Test: Récupérer une campagne avec son URL cible"""
        # Arrange
        campaign_id = "123e4567-e89b-12d3-a456-426614174000"
        expected_campaign = Campaign(
            id=campaign_id,
            name="Test Campaign",
            description="Test description",
            target_url="https://example.com",
            personaIds=["123e4567-e89b-12d3-a456-426614174001"],
            simulationConfig={
                "concurrentSessions": 5,
                "sessionInterval": 30,
                "duration": 60,
                "randomization": {
                    "enabled": True,
                    "timeVariation": 0.1,
                    "actionVariation": 0.1,
                    "pathVariation": 0.1,
                },
                "behaviorVariation": 0.1,
            },
            status="draft",
            metrics={
                "totalSessions": 0,
                "completedSessions": 0,
                "failedSessions": 0,
                "averageSessionDuration": 0,
                "totalPageViews": 0,
                "uniquePageViews": 0,
                "bounceRate": 0,
                "conversionRate": 0,
            },
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        
        campaign_service.db.query.return_value.filter.return_value.first.return_value = expected_campaign
        
        # Act
        result = campaign_service.get_campaign_by_id(campaign_id)
        
        # Assert
        assert result is not None
        assert result.target_url == "https://example.com"
        assert result.id == campaign_id

    def test_validate_target_url_format(self):
        """Test: Validation du format de l'URL cible"""
        from shared.schemas import CreateCampaignRequestSchema
        
        # URLs valides
        valid_urls = [
            "https://example.com",
            "http://localhost:3000",
            "https://subdomain.example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
            "https://example.com/path#fragment",
        ]
        
        for url in valid_urls:
            data = {
                "name": "Test Campaign",
                "description": "Test description",
                "target_url": url,
            "total_sessions": 5,
            "concurrent_sessions": 5,
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "rate_limit_delay_ms": 1000,
            "user_agent_rotation": True,
            "respect_robots_txt": True,
            }
            
            # Ne devrait pas lever d'exception
            CreateCampaignRequestSchema.parse(data)

    def test_validate_target_url_invalid_format(self):
        """Test: Validation des URLs invalides"""
        from shared.schemas import CreateCampaignRequestSchema
        
        # URLs invalides
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "file:///path/to/file",
            "javascript:alert('xss')",
            "",
            None,
        ]
        
        for url in invalid_urls:
            data = {
                "name": "Test Campaign",
                "description": "Test description",
                "target_url": url,
            "total_sessions": 5,
            "concurrent_sessions": 5,
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "rate_limit_delay_ms": 1000,
            "user_agent_rotation": True,
            "respect_robots_txt": True,
            }
            
            # Devrait lever une ValidationError
            with pytest.raises(ValidationError):
                CreateCampaignRequestSchema.parse(data)
