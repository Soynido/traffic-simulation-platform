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
import random

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.simulation_engine import SimulationEngine, SimulationConfig
from core.navigation_engine import NavigationEngine
from services.session_service import SessionService
from services.campaign_service import CampaignService
from services.persona_service import PersonaService
from utils.redis_client import RedisQueueClient as RedisClient
from utils.logger import setup_logging


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
        self.navigation_engine = None
        
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
            self.navigation_engine = NavigationEngine()
            
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
                task_type = task_data.get('type', 'simulation')
                
                if task_id and task_id not in self.current_tasks:
                    if task_type == 'campaign_navigation':
                        # Créer une tâche asynchrone pour la navigation de campagne
                        task = asyncio.create_task(self._execute_campaign_navigation_task(task_data))
                        self.current_tasks[task_id] = task
                        self.logger.info(f"Tâche de navigation de campagne {task_id} démarrée")
                    else:
                        # Créer une tâche asynchrone pour cette simulation
                        task = asyncio.create_task(self._execute_simulation_task(task_data))
                        self.current_tasks[task_id] = task
                        self.logger.info(f"Tâche de simulation {task_id} démarrée")
            
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
                # Construire la configuration depuis la tâche (enrichie par l'orchestrateur)
                config = SimulationConfig(
                    campaign_id=campaign_id,
                    persona_id=persona_id,
                    target_url=task_data.get('target_url') or task_data.get('start_url'),
                    max_pages=int(task_data.get('max_pages', 3)),
                    max_actions_per_page=int(task_data.get('max_actions_per_page', 10)),
                    session_duration_min=int(task_data.get('session_duration_min', 60)),
                    session_duration_max=int(task_data.get('session_duration_max', 120)),
                    scroll_probability=float(task_data.get('scroll_probability', 0.8)),
                    click_probability=float(task_data.get('click_probability', 0.6)),
                    typing_probability=float(task_data.get('typing_probability', 0.1)),
                    rate_limit_delay_ms=int(task_data.get('rate_limit_delay_ms', 1000)),
                    user_agent_rotation=bool(task_data.get('user_agent_rotation', True)),
                    respect_robots_txt=bool(task_data.get('respect_robots_txt', True)),
                )
                
                # Créer le moteur de simulation
                simulation_engine = SimulationEngine(session)
                
                # Utiliser la session existante fournie par l'orchestrateur
                session_id = task_data.get('session_id')
                if not session_id:
                    self.logger.error("Task missing session_id; aborting")
                    return
                
                # Exécuter la simulation sur cette session
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
    
    async def _execute_campaign_navigation_task(self, task_data: Dict[str, Any]):
        """Exécute une tâche de navigation de campagne."""
        task_id = task_data.get('id')
        campaign_id = task_data.get('campaign_id')
        
        try:
            self.logger.info(f"Exécution de la tâche de navigation de campagne {task_id} pour la campagne {campaign_id}")
            
            # Traiter la campagne avec navigation réelle
            result = await self.process_campaign_job(campaign_id)
            
            # Mettre à jour le statut de la tâche
            await self.redis_client.update_task_status(task_id, 'completed', {
                'campaign_id': campaign_id,
                'result': result
            })
            
            self.logger.info(f"Tâche de navigation de campagne {task_id} terminée avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de la tâche de navigation de campagne {task_id}: {e}")
            
            # Mettre à jour le statut de la tâche en cas d'erreur
            try:
                await self.redis_client.update_task_status(task_id, 'failed', {
                    'campaign_id': campaign_id,
                    'error': str(e)
                })
            except Exception as update_error:
                self.logger.error(f"Erreur lors de la mise à jour du statut de la tâche {task_id}: {update_error}")
    
    async def process_campaign_job(self, campaign_id: str) -> Dict[str, Any]:
        """
        Traite un job de campagne avec navigation réelle
        
        Args:
            campaign_id: ID de la campagne à traiter
            
        Returns:
            Résultats de la campagne
        """
        try:
            self.logger.info(f"Traitement de la campagne {campaign_id}")
            
            # Récupérer la campagne depuis la base de données
            async with self.session_factory() as session:
                campaign_service = CampaignService(session)
                campaign = await campaign_service.get_campaign_by_id(campaign_id)
                
                if not campaign:
                    raise Exception(f"Campagne {campaign_id} non trouvée")
                
                # Récupérer les personas de la campagne
                persona_service = PersonaService(session)
                personas = []
                for persona_id in campaign.personaIds:
                    persona = await persona_service.get_persona_by_id(persona_id)
                    if persona:
                        personas.append(persona)
                
                if not personas:
                    raise Exception(f"Aucun persona trouvé pour la campagne {campaign_id}")
                
                # Calculer le nombre de sessions et la durée
                sessions_count = campaign.simulationConfig.concurrentSessions
                duration_seconds = campaign.simulationConfig.duration * 60  # Convertir en secondes
                
                # Exécuter la campagne avec navigation réelle
                results = await self.navigation_engine.run_campaign(
                    campaign=campaign,
                    personas=personas,
                    sessions_count=sessions_count,
                    duration_seconds=duration_seconds
                )
                
                # Calculer les métriques
                successful_sessions = [r for r in results if r.get("success", False)]
                failed_sessions = [r for r in results if not r.get("success", False)]
                
                total_duration = sum(r.get("duration", 0) for r in successful_sessions)
                average_duration = total_duration / len(successful_sessions) if successful_sessions else 0
                
                total_page_views = sum(r.get("page_views", 0) for r in successful_sessions)
                total_actions = sum(r.get("actions", 0) for r in successful_sessions)
                
                # Mettre à jour les métriques de la campagne
                campaign_metrics = {
                    "totalSessions": len(results),
                    "completedSessions": len(successful_sessions),
                    "failedSessions": len(failed_sessions),
                    "averageSessionDuration": average_duration,
                    "totalPageViews": total_page_views,
                    "uniquePageViews": total_page_views,  # Approximation
                    "bounceRate": 0.0,  # À calculer plus précisément
                    "conversionRate": 0.0,  # À calculer plus précisément
                }
                
                # Mettre à jour la campagne
                await campaign_service.update_campaign(campaign_id, {
                    "metrics": campaign_metrics,
                    "status": "completed"
                })
                
                self.logger.info(f"Campagne {campaign_id} terminée: {len(successful_sessions)}/{len(results)} sessions réussies")
                
                return {
                    "campaign_id": campaign_id,
                    "status": "completed",
                    "metrics": campaign_metrics,
                    "results": results
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la campagne {campaign_id}: {e}")
            
            # Mettre à jour le statut de la campagne en cas d'erreur
            try:
                async with self.session_factory() as session:
                    campaign_service = CampaignService(session)
                    await campaign_service.update_campaign(campaign_id, {
                        "status": "error"
                    })
            except Exception as update_error:
                self.logger.error(f"Erreur lors de la mise à jour du statut de la campagne {campaign_id}: {update_error}")
            
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e)
            }
    
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
