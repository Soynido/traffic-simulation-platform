"""
Client Redis pour la gestion des tâches de simulation.
"""
import json
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
import redis.asyncio as redis


class RedisClient:
    """Client Redis pour la gestion des tâches."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        
        # Noms des queues
        self.pending_queue = "simulation:pending"
        self.processing_queue = "simulation:processing"
        self.completed_queue = "simulation:completed"
        self.failed_queue = "simulation:failed"
    
    async def connect(self):
        """Se connecter à Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            self.logger.info("Connexion à Redis établie")
        except Exception as e:
            self.logger.error(f"Erreur de connexion à Redis: {e}")
            raise
    
    async def close(self):
        """Fermer la connexion Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Connexion Redis fermée")
    
    async def add_task(self, task_data: Dict[str, Any]) -> str:
        """Ajouter une tâche à la queue."""
        try:
            task_id = task_data.get('id', f"task_{int(time.time() * 1000)}")
            task_data['id'] = task_id
            task_data['status'] = 'pending'
            task_data['created_at'] = time.time()
            
            # Ajouter à la queue des tâches en attente
            await self.redis_client.lpush(self.pending_queue, json.dumps(task_data))
            
            self.logger.info(f"Tâche {task_id} ajoutée à la queue")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de la tâche: {e}")
            raise
    
    async def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupérer les tâches en attente."""
        try:
            tasks = []
            
            for _ in range(limit):
                # Récupérer une tâche de la queue
                task_json = await self.redis_client.rpop(self.pending_queue)
                
                if not task_json:
                    break
                
                task_data = json.loads(task_json)
                tasks.append(task_data)
                
                # Déplacer vers la queue de traitement
                await self.redis_client.lpush(self.processing_queue, task_json)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des tâches: {e}")
            return []
    
    async def update_task_status(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None):
        """Mettre à jour le statut d'une tâche."""
        try:
            # Récupérer la tâche de la queue de traitement
            task_json = await self.redis_client.rpop(self.processing_queue)
            
            if not task_json:
                self.logger.warning(f"Tâche {task_id} non trouvée dans la queue de traitement")
                return
            
            task_data = json.loads(task_json)
            task_data['status'] = status
            task_data['updated_at'] = time.time()
            
            if result:
                task_data['result'] = result
            
            # Déplacer vers la queue appropriée
            if status == 'completed':
                await self.redis_client.lpush(self.completed_queue, json.dumps(task_data))
            elif status == 'failed':
                await self.redis_client.lpush(self.failed_queue, json.dumps(task_data))
            
            self.logger.info(f"Statut de la tâche {task_id} mis à jour: {status}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du statut de la tâche {task_id}: {e}")
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'une tâche."""
        try:
            # Chercher dans toutes les queues
            queues = [self.pending_queue, self.processing_queue, self.completed_queue, self.failed_queue]
            
            for queue in queues:
                tasks = await self.redis_client.lrange(queue, 0, -1)
                
                for task_json in tasks:
                    task_data = json.loads(task_json)
                    if task_data.get('id') == task_id:
                        return task_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du statut de la tâche {task_id}: {e}")
            return None
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Obtenir les statistiques des queues."""
        try:
            stats = {}
            
            queues = {
                'pending': self.pending_queue,
                'processing': self.processing_queue,
                'completed': self.completed_queue,
                'failed': self.failed_queue
            }
            
            for name, queue in queues.items():
                length = await self.redis_client.llen(queue)
                stats[name] = length
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
    
    async def clear_queue(self, queue_name: str):
        """Vider une queue."""
        try:
            await self.redis_client.delete(queue_name)
            self.logger.info(f"Queue {queue_name} vidée")
        except Exception as e:
            self.logger.error(f"Erreur lors du vidage de la queue {queue_name}: {e}")
    
    async def clear_all_queues(self):
        """Vider toutes les queues."""
        try:
            queues = [self.pending_queue, self.processing_queue, self.completed_queue, self.failed_queue]
            
            for queue in queues:
                await self.redis_client.delete(queue)
            
            self.logger.info("Toutes les queues vidées")
        except Exception as e:
            self.logger.error(f"Erreur lors du vidage des queues: {e}")
    
    async def get_failed_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupérer les tâches échouées."""
        try:
            tasks = []
            task_jsons = await self.redis_client.lrange(self.failed_queue, 0, limit - 1)
            
            for task_json in task_jsons:
                task_data = json.loads(task_json)
                tasks.append(task_data)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des tâches échouées: {e}")
            return []
    
    async def retry_failed_task(self, task_id: str) -> bool:
        """Réessayer une tâche échouée."""
        try:
            # Récupérer la tâche de la queue des échecs
            task_json = await self.redis_client.rpop(self.failed_queue)
            
            if not task_json:
                return False
            
            task_data = json.loads(task_json)
            
            if task_data.get('id') != task_id:
                # Remettre la tâche dans la queue
                await self.redis_client.lpush(self.failed_queue, task_json)
                return False
            
            # Réinitialiser le statut
            task_data['status'] = 'pending'
            task_data['retry_count'] = task_data.get('retry_count', 0) + 1
            task_data['updated_at'] = time.time()
            
            # Ajouter à la queue des tâches en attente
            await self.redis_client.lpush(self.pending_queue, json.dumps(task_data))
            
            self.logger.info(f"Tâche {task_id} remise en queue pour réessai")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du réessai de la tâche {task_id}: {e}")
            return False
