"""
Tests de performance pour la Traffic Simulation Platform.
Vérifie les performances de l'API et de la base de données.
"""
import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ..models import Persona, Campaign, Session
from ..services import PersonaService, CampaignService, SessionService
from ..database.connection import get_db_session


class PerformanceTestSuite:
    """Suite de tests de performance."""
    
    @pytest.fixture
    async def db_engine(self):
        """Créer un moteur de base de données pour les tests."""
        database_url = "postgresql+asyncpg://traffic_user:traffic_pass@localhost:5432/traffic_test"
        engine = create_async_engine(database_url, echo=False)
        yield engine
        await engine.dispose()
    
    @pytest.fixture
    async def db_session(self, db_engine):
        """Créer une session de base de données."""
        async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            yield session
    
    async def test_persona_creation_performance(self, db_session):
        """Test de performance pour la création de personas."""
        service = PersonaService(db_session)
        
        # Mesurer le temps de création de 100 personas
        start_time = time.time()
        
        personas = []
        for i in range(100):
            persona_data = {
                'name': f'Test Persona {i}',
                'description': f'Description for persona {i}',
                'session_duration_min': 60,
                'session_duration_max': 120,
                'pages_min': 1,
                'pages_max': 5,
                'actions_per_page_min': 1,
                'actions_per_page_max': 10,
                'scroll_probability': 0.8,
                'click_probability': 0.6,
                'typing_probability': 0.1
            }
            persona = await service.create_persona(persona_data)
            personas.append(persona)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Vérifier que la création est rapide (moins de 5 secondes pour 100 personas)
        assert total_time < 5.0, f"Persona creation took {total_time:.2f}s, expected < 5.0s"
        
        # Vérifier que toutes les personas ont été créées
        assert len(personas) == 100
        
        # Nettoyage
        for persona in personas:
            await service.delete_persona(persona.id)
    
    async def test_campaign_creation_performance(self, db_session):
        """Test de performance pour la création de campagnes."""
        # Créer une persona d'abord
        persona_service = PersonaService(db_session)
        persona_data = {
            'name': 'Performance Test Persona',
            'session_duration_min': 60,
            'session_duration_max': 120,
            'pages_min': 1,
            'pages_max': 5
        }
        persona = await persona_service.create_persona(persona_data)
        
        service = CampaignService(db_session)
        
        # Mesurer le temps de création de 50 campagnes
        start_time = time.time()
        
        campaigns = []
        for i in range(50):
            campaign_data = {
                'name': f'Performance Test Campaign {i}',
                'description': f'Description for campaign {i}',
                'target_url': f'https://example{i}.com',
                'total_sessions': 100,
                'concurrent_sessions': 10,
                'persona_id': str(persona.id),
                'rate_limit_delay_ms': 1000,
                'user_agent_rotation': True,
                'respect_robots_txt': True
            }
            campaign = await service.create_campaign(campaign_data)
            campaigns.append(campaign)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Vérifier que la création est rapide (moins de 3 secondes pour 50 campagnes)
        assert total_time < 3.0, f"Campaign creation took {total_time:.2f}s, expected < 3.0s"
        
        # Vérifier que toutes les campagnes ont été créées
        assert len(campaigns) == 50
        
        # Nettoyage
        for campaign in campaigns:
            await service.delete_campaign(campaign.id)
        await persona_service.delete_persona(persona.id)
    
    async def test_session_creation_performance(self, db_session):
        """Test de performance pour la création de sessions."""
        # Créer une persona et une campagne d'abord
        persona_service = PersonaService(db_session)
        persona_data = {
            'name': 'Performance Test Persona',
            'session_duration_min': 60,
            'session_duration_max': 120,
            'pages_min': 1,
            'pages_max': 5
        }
        persona = await persona_service.create_persona(persona_data)
        
        campaign_service = CampaignService(db_session)
        campaign_data = {
            'name': 'Performance Test Campaign',
            'target_url': 'https://example.com',
            'total_sessions': 1000,
            'concurrent_sessions': 10,
            'persona_id': str(persona.id)
        }
        campaign = await campaign_service.create_campaign(campaign_data)
        
        service = SessionService(db_session)
        
        # Mesurer le temps de création de 500 sessions
        start_time = time.time()
        
        sessions = []
        for i in range(500):
            session_data = {
                'campaign_id': str(campaign.id),
                'persona_id': str(persona.id),
                'start_url': f'https://example.com/page{i}',
                'user_agent': f'Mozilla/5.0 Test Browser {i}',
                'viewport_width': 1920,
                'viewport_height': 1080
            }
            session = await service.create_session(session_data)
            sessions.append(session)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Vérifier que la création est rapide (moins de 10 secondes pour 500 sessions)
        assert total_time < 10.0, f"Session creation took {total_time:.2f}s, expected < 10.0s"
        
        # Vérifier que toutes les sessions ont été créées
        assert len(sessions) == 500
        
        # Nettoyage
        for session in sessions:
            await service.delete_session(session.id)
        await campaign_service.delete_campaign(campaign.id)
        await persona_service.delete_persona(persona.id)
    
    async def test_database_query_performance(self, db_session):
        """Test de performance pour les requêtes de base de données."""
        # Créer des données de test
        persona_service = PersonaService(db_session)
        personas = []
        
        for i in range(100):
            persona_data = {
                'name': f'Query Test Persona {i}',
                'session_duration_min': 60,
                'session_duration_max': 120,
                'pages_min': 1,
                'pages_max': 5
            }
            persona = await persona_service.create_persona(persona_data)
            personas.append(persona)
        
        # Test de performance pour la récupération de toutes les personas
        start_time = time.time()
        all_personas = await persona_service.get_all_personas(limit=1000)
        end_time = time.time()
        query_time = end_time - start_time
        
        # Vérifier que la requête est rapide (moins de 1 seconde)
        assert query_time < 1.0, f"Persona query took {query_time:.2f}s, expected < 1.0s"
        
        # Vérifier que toutes les personas ont été récupérées
        assert len(all_personas) >= 100
        
        # Test de performance pour la recherche par nom
        start_time = time.time()
        search_results = await persona_service.get_all_personas(name_filter="Query Test")
        end_time = time.time()
        search_time = end_time - start_time
        
        # Vérifier que la recherche est rapide (moins de 0.5 seconde)
        assert search_time < 0.5, f"Persona search took {search_time:.2f}s, expected < 0.5s"
        
        # Vérifier que les résultats de recherche sont corrects
        assert len(search_results) >= 100
        
        # Nettoyage
        for persona in personas:
            await persona_service.delete_persona(persona.id)
    
    async def test_concurrent_operations_performance(self, db_session):
        """Test de performance pour les opérations concurrentes."""
        # Créer une persona d'abord
        persona_service = PersonaService(db_session)
        persona_data = {
            'name': 'Concurrent Test Persona',
            'session_duration_min': 60,
            'session_duration_max': 120,
            'pages_min': 1,
            'pages_max': 5
        }
        persona = await persona_service.create_persona(persona_data)
        
        # Test de performance pour les opérations concurrentes
        async def create_campaign(i):
            campaign_service = CampaignService(db_session)
            campaign_data = {
                'name': f'Concurrent Campaign {i}',
                'target_url': f'https://example{i}.com',
                'total_sessions': 100,
                'concurrent_sessions': 10,
                'persona_id': str(persona.id)
            }
            return await campaign_service.create_campaign(campaign_data)
        
        # Mesurer le temps de création concurrente de 20 campagnes
        start_time = time.time()
        
        tasks = [create_campaign(i) for i in range(20)]
        campaigns = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Vérifier que les opérations concurrentes sont rapides (moins de 2 secondes)
        assert total_time < 2.0, f"Concurrent operations took {total_time:.2f}s, expected < 2.0s"
        
        # Vérifier que toutes les campagnes ont été créées
        assert len(campaigns) == 20
        
        # Nettoyage
        campaign_service = CampaignService(db_session)
        for campaign in campaigns:
            await campaign_service.delete_campaign(campaign.id)
        await persona_service.delete_persona(persona.id)
    
    async def test_memory_usage_performance(self, db_session):
        """Test de performance pour l'utilisation mémoire."""
        import psutil
        import os
        
        # Obtenir l'utilisation mémoire initiale
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Créer beaucoup de données
        persona_service = PersonaService(db_session)
        personas = []
        
        for i in range(1000):
            persona_data = {
                'name': f'Memory Test Persona {i}',
                'session_duration_min': 60,
                'session_duration_max': 120,
                'pages_min': 1,
                'pages_max': 5
            }
            persona = await persona_service.create_persona(persona_data)
            personas.append(persona)
        
        # Obtenir l'utilisation mémoire après création
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Vérifier que l'augmentation mémoire est raisonnable (moins de 100 MB)
        assert memory_increase < 100, f"Memory increase was {memory_increase:.2f}MB, expected < 100MB"
        
        # Nettoyage
        for persona in personas:
            await persona_service.delete_persona(persona.id)
    
    async def test_api_response_time_performance(self):
        """Test de performance pour les temps de réponse API."""
        import httpx
        
        # Test de performance pour les endpoints API
        endpoints = [
            'http://localhost:8000/health',
            'http://localhost:8000/api/v1/personas',
            'http://localhost:8000/api/v1/campaigns',
            'http://localhost:8000/api/v1/sessions',
            'http://localhost:8000/api/v1/analytics'
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                # Mesurer le temps de réponse
                start_time = time.time()
                
                try:
                    response = await client.get(endpoint)
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    # Vérifier que la réponse est rapide (moins de 200ms)
                    assert response_time < 0.2, f"API endpoint {endpoint} took {response_time:.3f}s, expected < 0.2s"
                    
                    # Vérifier que la réponse est valide
                    assert response.status_code in [200, 404], f"API endpoint {endpoint} returned status {response.status_code}"
                    
                except httpx.ConnectError:
                    # Ignorer les erreurs de connexion si l'API n'est pas démarrée
                    pass
