"""
Tests unitaires pour la navigation Playwright dans les simulation workers
Approche TDD : Tests d'abord, implémentation ensuite
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime

# Import des types partagés
from shared.types import Campaign, Session, Persona

# Import des services à implémenter
from core.navigation_engine import NavigationEngine
from workers.simulation_worker import SimulationWorker


class TestPlaywrightNavigation:
    """Tests pour la navigation Playwright"""
    
    @pytest.fixture
    def navigation_engine(self):
        """Fixture pour créer une instance du moteur de navigation"""
        return NavigationEngine()
    
    @pytest.fixture
    def sample_campaign(self):
        """Campagne d'exemple avec target_url"""
        return Campaign(
            id="123e4567-e89b-12d3-a456-426614174000",
            name="Test Campaign",
            description="Test campaign for navigation",
            targetUrl="https://example.com",
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
            status="running",
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
    
    @pytest.fixture
    def sample_persona(self):
        """Persona d'exemple"""
        return Persona(
            id="123e4567-e89b-12d3-a456-426614174001",
            name="Test Persona",
            description="Test persona for navigation",
            behaviorProfile={
                "browsingSpeed": "normal",
                "clickPattern": "systematic",
                "scrollBehavior": "smooth",
                "sessionDuration": {"min": 5, "max": 30},
                "pageViewsPerSession": {"min": 3, "max": 10},
                "timeOnPage": {"min": 10, "max": 120},
            },
            demographics={
                "age": {"min": 25, "max": 45},
                "gender": "prefer_not_to_say",
                "location": {"country": "US"},
                "interests": ["technology"],
            },
            technicalProfile={
                "deviceTypes": [{"type": "desktop", "probability": 1.0}],
                "browsers": [{"name": "Chrome", "version": "120", "userAgent": "", "probability": 1.0}],
                "operatingSystems": [{"name": "Windows", "version": "10", "probability": 1.0}],
                "screenResolutions": [{"width": 1920, "height": 1080, "probability": 1.0}],
                "connectionTypes": [{"type": "wifi", "speed": "fast", "probability": 1.0}],
                "timezone": "UTC",
            },
            isActive=True,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_run_session_success(self, navigation_engine, sample_campaign, sample_persona):
        """Test: Exécuter une session de navigation avec succès"""
        # Arrange
        target_url = sample_campaign.targetUrl
        duration_seconds = 5
        
        with patch('core.navigation_engine.sync_playwright') as mock_playwright:
            mock_browser = Mock()
            mock_page = Mock()
            mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Act
            result = await navigation_engine.run_session(
                target_url=target_url,
                duration_seconds=duration_seconds,
                persona=sample_persona
            )
            
            # Assert
            assert result is not None
            assert result["success"] is True
            assert result["url"] == target_url
            assert result["duration"] >= duration_seconds
            mock_page.goto.assert_called_once_with(target_url, wait_until="networkidle")
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_session_network_error(self, navigation_engine, sample_persona):
        """Test: Gérer une erreur de réseau lors de la navigation"""
        # Arrange
        target_url = "https://nonexistent-domain-12345.com"
        duration_seconds = 5
        
        with patch('core.navigation_engine.sync_playwright') as mock_playwright:
            mock_browser = Mock()
            mock_page = Mock()
            mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.goto.side_effect = Exception("Network error")
            
            # Act
            result = await navigation_engine.run_session(
                target_url=target_url,
                duration_seconds=duration_seconds,
                persona=sample_persona
            )
            
            # Assert
            assert result is not None
            assert result["success"] is False
            assert "error" in result
            assert result["url"] == target_url
            mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_campaign_multiple_sessions(self, navigation_engine, sample_campaign, sample_persona):
        """Test: Exécuter une campagne avec plusieurs sessions"""
        # Arrange
        target_url = sample_campaign.targetUrl
        sessions_count = 3
        duration_seconds = 2
        
        with patch('core.navigation_engine.sync_playwright') as mock_playwright:
            mock_browser = Mock()
            mock_page = Mock()
            mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Act
            results = await navigation_engine.run_campaign(
                campaign=sample_campaign,
                personas=[sample_persona],
                sessions_count=sessions_count,
                duration_seconds=duration_seconds
            )
            
            # Assert
            assert len(results) == sessions_count
            for result in results:
                assert result["success"] is True
                assert result["url"] == target_url

    @pytest.mark.asyncio
    async def test_run_campaign_with_different_personas(self, navigation_engine, sample_campaign):
        """Test: Exécuter une campagne avec différents personas"""
        # Arrange
        personas = [
            Persona(
                id=f"persona-{i}",
                name=f"Persona {i}",
                description=f"Test persona {i}",
                behaviorProfile={
                    "browsingSpeed": "normal",
                    "clickPattern": "systematic",
                    "scrollBehavior": "smooth",
                    "sessionDuration": {"min": 5, "max": 30},
                    "pageViewsPerSession": {"min": 3, "max": 10},
                    "timeOnPage": {"min": 10, "max": 120},
                },
                demographics={
                    "age": {"min": 25, "max": 45},
                    "gender": "prefer_not_to_say",
                    "location": {"country": "US"},
                    "interests": ["technology"],
                },
                technicalProfile={
                    "deviceTypes": [{"type": "desktop", "probability": 1.0}],
                    "browsers": [{"name": "Chrome", "version": "120", "userAgent": "", "probability": 1.0}],
                    "operatingSystems": [{"name": "Windows", "version": "10", "probability": 1.0}],
                    "screenResolutions": [{"width": 1920, "height": 1080, "probability": 1.0}],
                    "connectionTypes": [{"type": "wifi", "speed": "fast", "probability": 1.0}],
                    "timezone": "UTC",
                },
                isActive=True,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
            )
            for i in range(2)
        ]
        
        with patch('core.navigation_engine.sync_playwright') as mock_playwright:
            mock_browser = Mock()
            mock_page = Mock()
            mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Act
            results = await navigation_engine.run_campaign(
                campaign=sample_campaign,
                personas=personas,
                sessions_count=2,
                duration_seconds=2
            )
            
            # Assert
            assert len(results) == 2
            for result in results:
                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_navigation_engine_initialization(self):
        """Test: Initialisation du moteur de navigation"""
        # Act
        engine = NavigationEngine()
        
        # Assert
        assert engine is not None
        assert hasattr(engine, 'run_session')
        assert hasattr(engine, 'run_campaign')

    @pytest.mark.asyncio
    async def test_run_session_with_user_agent(self, navigation_engine, sample_persona):
        """Test: Exécuter une session avec un user agent spécifique"""
        # Arrange
        target_url = "https://example.com"
        duration_seconds = 5
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        with patch('core.navigation_engine.sync_playwright') as mock_playwright:
            mock_browser = Mock()
            mock_page = Mock()
            mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Act
            result = await navigation_engine.run_session(
                target_url=target_url,
                duration_seconds=duration_seconds,
                persona=sample_persona,
                user_agent=user_agent
            )
            
            # Assert
            assert result is not None
            assert result["success"] is True
            mock_page.set_extra_http_headers.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_session_with_viewport(self, navigation_engine, sample_persona):
        """Test: Exécuter une session avec une taille de viewport spécifique"""
        # Arrange
        target_url = "https://example.com"
        duration_seconds = 5
        viewport = {"width": 1920, "height": 1080}
        
        with patch('core.navigation_engine.sync_playwright') as mock_playwright:
            mock_browser = Mock()
            mock_page = Mock()
            mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Act
            result = await navigation_engine.run_session(
                target_url=target_url,
                duration_seconds=duration_seconds,
                persona=sample_persona,
                viewport=viewport
            )
            
            # Assert
            assert result is not None
            assert result["success"] is True
            mock_page.set_viewport_size.assert_called_once_with(viewport)

    @pytest.mark.asyncio
    async def test_run_session_timeout_handling(self, navigation_engine, sample_persona):
        """Test: Gérer les timeouts lors de la navigation"""
        # Arrange
        target_url = "https://example.com"
        duration_seconds = 5
        
        with patch('core.navigation_engine.sync_playwright') as mock_playwright:
            mock_browser = Mock()
            mock_page = Mock()
            mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.goto.side_effect = Exception("Timeout")
            
            # Act
            result = await navigation_engine.run_session(
                target_url=target_url,
                duration_seconds=duration_seconds,
                persona=sample_persona
            )
            
            # Assert
            assert result is not None
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_simulation_worker_integration(self, sample_campaign, sample_persona):
        """Test: Intégration avec le simulation worker"""
        # Arrange
        mock_db = Mock()
        mock_redis = Mock()
        worker = SimulationWorker(db=mock_db, redis=mock_redis)
        
        with patch('workers.simulation_worker.NavigationEngine') as mock_nav_engine:
            mock_engine_instance = Mock()
            mock_nav_engine.return_value = mock_engine_instance
            mock_engine_instance.run_campaign = AsyncMock(return_value=[
                {"success": True, "url": "https://example.com", "duration": 5}
            ])
            
            # Act
            result = await worker.process_campaign_job(sample_campaign.id)
            
            # Assert
            assert result is not None
            mock_engine_instance.run_campaign.assert_called_once()
