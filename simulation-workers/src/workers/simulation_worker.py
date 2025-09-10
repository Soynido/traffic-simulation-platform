"""
Worker principal de simulation pour la Traffic Simulation Platform.
Gère l'exécution des tâches de simulation en arrière-plan.
"""
import asyncio
import logging
import signal
import sys
from typing import Dict, Any, Optional
import json
import time

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ..core.simulation_engine import SimulationEngine, SimulationConfig
from ..services import PersonaService, CampaignService, SessionService
from ..utils.redis_client import RedisClient
from ..utils.logger import setup_logging


class SimulationWorker:
    """Worker principal de simulation."""
    
    def __init__(self, worker_id: str, config: Dict[str, Any]):
        self.worker_id = worker_id
        self.config = config
        self.logger = setup_logging(f"simulation_worker_{worker_id}")
        
        # Configuration de la base de données
        self.database_url = config.get('database_url', 'postgresql+asyncpg://traffic_user:traffic_pass@localhost:5432/traffic_db')
        self.redis_url = config.get('redis_url', 'redis://localhost:6379')
        
        # Services
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        self.simulation_engine = None
        
        # État du worker
        self.running = False
        self.current_tasks = {}
        
        # Configuration des signaux
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Configure les gestionnaires de signaux pour l'arrêt propre."""
        def signal_handler(signum, frame):
            self.logger.info(f"Signal {signum} reçu, arrêt du worker...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self):
        """Initialise le worker."""
        try:
            self.logger.info(f"Initialisation du worker {self.worker_id}...")
            
            # Initialiser la base de données
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_size=10,
                max_overflow=20
            )
            
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialiser Redis
            self.redis_client = RedisClient(self.redis_url)
            await self.redis_client.connect()
            
            # Initialiser le moteur de simulation
            async with self.session_factory() as session:
                self.simulation_engine = SimulationEngine(session)
            
            self.logger.info(f"Worker {self.worker_id} initialisé avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du worker {self.worker_id}: {e}")
            raise
    
    async def start(self):
        """Démarre le worker."""
        try:
            await self.initialize()
            self.running = True
            
            self.logger.info(f"Démarrage du worker {self.worker_id}...")
            
            # Boucle principale
            while self.running:
                try:
                    # Traiter les tâches en attente
                    await self._process_pending_tasks()
                    
                    # Nettoyer les tâches terminées
                    await self._cleanup_completed_tasks()
                    
                    # Attendre avant la prochaine itération
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Erreur dans la boucle principale du worker {self.worker_id}: {e}")
                    await asyncio.sleep(5)  # Attendre avant de réessayer
            
            self.logger.info(f"Worker {self.worker_id} arrêté")
            
        except Exception as e:
            self.logger.error(f"Erreur fatale dans le worker {self.worker_id}: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def stop(self):
        """Arrête le worker."""
        self.logger.info(f"Arrêt du worker {self.worker_id}...")
        self.running = False
        
        # Annuler toutes les tâches en cours
        for task_id, task in self.current_tasks.items():
            if not task.done():
                task.cancel()
                self.logger.info(f"Tâche {task_id} annulée")
    
    async def cleanup(self):
        """Nettoie les ressources du worker."""
        try:
            # Fermer Redis
            if self.redis_client:
                await self.redis_client.close()
            
            # Fermer la base de données
            if self.engine:
                await self.engine.dispose()
            
            self.logger.info(f"Worker {self.worker_id} nettoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage du worker {self.worker_id}: {e}")
    
    async def _process_pending_tasks(self):
        """Traite les tâches en attente."""
        try:
            # Récupérer les tâches en attente depuis Redis
            tasks = await self.redis_client.get_pending_tasks(limit=10)
            
            for task_data in tasks:
                task_id = task_data.get('id')
                
                if task_id and task_id not in self.current_tasks:
                    # Créer une tâche asynchrone pour cette simulation
                    task = asyncio.create_task(self._execute_simulation_task(task_data))
                    self.current_tasks[task_id] = task
                    
                    self.logger.info(f"Tâche {task_id} démarrée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement des tâches: {e}")
    
    async def _execute_simulation_task(self, task_data: Dict[str, Any]):
        """Exécute une tâche de simulation."""
        task_id = task_data.get('id')
        campaign_id = task_data.get('campaign_id')
        persona_id = task_data.get('persona_id')
        
        try:
            self.logger.info(f"Exécution de la tâche {task_id} pour la campagne {campaign_id}")
            
            # Créer une session de base de données
            async with self.session_factory() as session:
                # Récupérer les données de la campagne et de la persona
                campaign_service = CampaignService(session)
                persona_service = PersonaService(session)
                
                campaign = await campaign_service.get_campaign(campaign_id)
                persona = await persona_service.get_persona(persona_id)
                
                if not campaign or not persona:
                    self.logger.error(f"Campagne {campaign_id} ou persona {persona_id} non trouvée")
                    return
                
                # Créer la configuration de simulation
                config = SimulationConfig(
                    campaign_id=campaign_id,
                    persona_id=persona_id,
                    target_url=campaign.target_url,
                    max_pages=random.randint(persona.pages_min, persona.pages_max),
                    max_actions_per_page=random.randint(persona.actions_per_page_min, persona.actions_per_page_max),
                    session_duration_min=persona.session_duration_min,
                    session_duration_max=persona.session_duration_max,
                    scroll_probability=persona.scroll_probability,
                    click_probability=persona.click_probability,
                    typing_probability=persona.typing_probability,
                    rate_limit_delay_ms=campaign.rate_limit_delay_ms,
                    user_agent_rotation=campaign.user_agent_rotation,
                    respect_robots_txt=campaign.respect_robots_txt
                )
                
                # Créer le moteur de simulation
                simulation_engine = SimulationEngine(session)
                
                # Démarrer la simulation
                session_id = await simulation_engine.start_simulation(config)
                
                # Attendre la fin de la simulation
                result = await simulation_engine._run_simulation(session_id, config)
                
                # Mettre à jour le statut de la tâche
                await self.redis_client.update_task_status(task_id, 'completed', {
                    'session_id': session_id,
                    'result': {
                        'status': result.status.value,
                        'pages_visited': result.pages_visited,
                        'actions_performed': result.actions_performed,
                        'total_duration': result.total_duration,
                        'rhythm_score': result.rhythm_score,
                        'detection_risk': result.detection_risk
                    }
                })
                
                self.logger.info(f"Tâche {task_id} terminée avec succès")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de la tâche {task_id}: {e}")
            
            # Mettre à jour le statut de la tâche en cas d'erreur
            try:
                await self.redis_client.update_task_status(task_id, 'failed', {
                    'error': str(e)
                })
            except Exception as update_error:
                self.logger.error(f"Erreur lors de la mise à jour du statut de la tâche {task_id}: {update_error}")
    
    async def _cleanup_completed_tasks(self):
        """Nettoie les tâches terminées."""
        completed_tasks = []
        
        for task_id, task in self.current_tasks.items():
            if task.done():
                completed_tasks.append(task_id)
                
                # Vérifier s'il y a eu une exception
                try:
                    await task
                except Exception as e:
                    self.logger.error(f"Tâche {task_id} terminée avec erreur: {e}")
        
        # Supprimer les tâches terminées
        for task_id in completed_tasks:
            del self.current_tasks[task_id]
    
    async def get_status(self) -> Dict[str, Any]:
        """Obtient le statut du worker."""
        return {
            'worker_id': self.worker_id,
            'running': self.running,
            'current_tasks': len(self.current_tasks),
            'task_ids': list(self.current_tasks.keys()),
            'database_connected': self.engine is not None,
            'redis_connected': self.redis_client is not None if self.redis_client else False
        }


async def main():
    """Point d'entrée principal du worker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulation Worker')
    parser.add_argument('--worker-id', required=True, help='ID du worker')
    parser.add_argument('--database-url', help='URL de la base de données')
    parser.add_argument('--redis-url', help='URL de Redis')
    parser.add_argument('--log-level', default='INFO', help='Niveau de log')
    
    args = parser.parse_args()
    
    # Configuration du worker
    config = {
        'database_url': args.database_url or 'postgresql+asyncpg://traffic_user:traffic_pass@localhost:5432/traffic_db',
        'redis_url': args.redis_url or 'redis://localhost:6379',
        'log_level': args.log_level
    }
    
    # Créer et démarrer le worker
    worker = SimulationWorker(args.worker_id, config)
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"Erreur fatale: {e}")
        sys.exit(1)
    finally:
        await worker.cleanup()


if __name__ == '__main__':
    asyncio.run(main())