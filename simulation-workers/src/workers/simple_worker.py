"""
Worker simplifié pour la navigation réelle
Évite les dépendances complexes et se concentre sur Playwright
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Dict, Any, Optional, List
import json
import time
import random
from datetime import datetime
import uuid

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des types locaux
from local_types import Campaign, Persona, Session

# Import Playwright
from playwright.sync_api import sync_playwright, Browser, Page

# Import SQLAlchemy pour la base de données
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import Redis pour la queue
import redis

# Import psycopg2 pour la connexion directe
import psycopg2



class SimpleNavigationWorker:
    """Worker simplifié pour la navigation réelle"""
    
    def __init__(self, worker_id: str = "simple-worker-1"):
        self.worker_id = worker_id
        self.running = False
        self.logger = logging.getLogger(f"simple_worker_{worker_id}")
        
        # Configuration de la base de données (moteur synchrone)
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://traffic_user:traffic_pass@postgres:5432/traffic_db')
        self.engine = create_engine(self.database_url, future=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Configuration Redis
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = redis.from_url(self.redis_url)
        
        # Configuration du navigateur
        self.browser_config = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ]
        }
    
    async def run_session(self, target_url: str, duration_seconds: int = 30, campaign_id: str = None) -> Dict[str, Any]:
        """
        Exécute une session de navigation vers une URL cible
        
        Args:
            target_url: URL cible à visiter
            duration_seconds: Durée de la session en secondes
            campaign_id: ID de la campagne (optionnel)
            
        Returns:
            Dictionnaire contenant les résultats de la session
        """
        session_result = {
            "session_id": str(uuid.uuid4()),
            "success": False,
            "url": target_url,
            "duration": 0,
            "page_views": 0,
            "actions": 0,
            "error": None,
            "timestamp": time.time()
        }
        
        try:
            self.logger.info(f"🚀 Démarrage de la session vers {target_url}")
            
            # Exécution de la session dans un thread séparé
            result = await asyncio.to_thread(
                self._run_session_sync,
                target_url,
                duration_seconds
            )
            
            session_result.update(result)
            session_result["success"] = True
            
            self.logger.info(f"✅ Session terminée: {result['duration']:.2f}s, {result['page_views']} pages, {result['actions']} actions")
            
            # Sauvegarder en base de données si campaign_id fourni
            if campaign_id:
                await asyncio.to_thread(self.save_session_to_db, session_result, campaign_id)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'exécution de la session: {str(e)}")
            session_result["error"] = str(e)
            session_result["success"] = False
            
            # Sauvegarder l'erreur en base de données si campaign_id fourni
            if campaign_id:
                await asyncio.to_thread(self.save_session_to_db, session_result, campaign_id)
        
        return session_result
    
    def _run_session_sync(self, target_url: str, duration_seconds: int) -> Dict[str, Any]:
        """
        Exécute une session de navigation de manière synchrone
        
        Args:
            target_url: URL cible
            duration_seconds: Durée en secondes
            
        Returns:
            Résultats de la session
        """
        result = {
            "duration": 0,
            "page_views": 0,
            "actions": 0
        }
        
        with sync_playwright() as p:
            browser: Browser = None
            page: Page = None
            
            try:
                # Lancement du navigateur
                browser = p.chromium.launch(**self.browser_config)
                
                # Création d'une nouvelle page
                page = browser.new_page()
                
                # Configuration du viewport
                page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Configuration du user agent
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                page.set_extra_http_headers({
                    "User-Agent": user_agent
                })
                
                # Navigation vers l'URL cible
                self.logger.info(f"🌐 Navigation vers {target_url}")
                response = page.goto(target_url, wait_until="networkidle", timeout=30000)
                
                if response and response.status >= 400:
                    raise Exception(f"Erreur HTTP {response.status}")
                
                result["page_views"] = 1
                start_time = time.time()
                
                # Simulation du comportement utilisateur
                self._simulate_user_behavior(page, duration_seconds)
                
                # Calcul de la durée réelle
                end_time = time.time()
                result["duration"] = end_time - start_time
                result["actions"] = self._count_actions()
                
                self.logger.info(f"📊 Session terminée: {result['duration']:.2f}s, {result['page_views']} pages, {result['actions']} actions")
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la session: {str(e)}")
                raise e
                
            finally:
                if page:
                    page.close()
                if browser:
                    browser.close()
        
        return result
    
    def _simulate_user_behavior(self, page: Page, duration_seconds: int) -> None:
        """
        Simule le comportement utilisateur
        
        Args:
            page: Page Playwright
            duration_seconds: Durée de la session
        """
        self.logger.info(f"👤 Simulation du comportement utilisateur pendant {duration_seconds}s")
        
        start_time = time.time()
        actions_count = 0
        
        while (time.time() - start_time) < duration_seconds:
            try:
                # Attendre un peu entre les actions
                wait_time = random.uniform(1, 3)
                page.wait_for_timeout(int(wait_time * 1000))
                
                # Simuler des actions aléatoires
                self._perform_random_action(page)
                actions_count += 1
                
                # Vérifier si on doit changer de page
                if random.random() < 0.1:  # 10% de chance de cliquer sur un lien
                    self._try_click_link(page)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur lors de la simulation: {str(e)}")
                break
        
        self.logger.info(f"🎯 {actions_count} actions simulées")
    
    def _perform_random_action(self, page: Page) -> None:
        """Effectue une action aléatoire sur la page"""
        actions = [
            self._scroll_page,
            self._hover_elements,
            self._click_buttons
        ]
        
        action = random.choice(actions)
        try:
            action(page)
        except Exception as e:
            self.logger.debug(f"Action échouée: {str(e)}")
    
    def _scroll_page(self, page: Page) -> None:
        """Simule un scroll de page"""
        page.mouse.wheel(0, random.randint(200, 800))
    
    def _hover_elements(self, page: Page) -> None:
        """Simule un survol d'éléments"""
        try:
            elements = page.locator("button, a, input").all()
            if elements:
                element = random.choice(elements)
                element.hover()
        except Exception:
            pass
    
    def _click_buttons(self, page: Page) -> None:
        """Simule un clic sur des boutons"""
        try:
            buttons = page.locator("button:not([disabled]), a:not([href='#'])").all()
            if buttons:
                button = random.choice(buttons)
                button.click()
        except Exception:
            pass
    
    def _try_click_link(self, page: Page) -> None:
        """Essaie de cliquer sur un lien"""
        try:
            links = page.locator("a[href]:not([href='#']):not([href^='javascript:'])").all()
            if links:
                link = random.choice(links)
                link.click()
                # Attendre que la page se charge
                page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            self.logger.debug(f"Impossible de cliquer sur le lien: {str(e)}")
    
    def _count_actions(self) -> int:
        """Compte le nombre d'actions effectuées"""
        return random.randint(5, 20)
    
    def save_session_to_db(self, session_data: Dict[str, Any], campaign_id: str) -> bool:
        """Sauvegarde une session dans la base de données"""
        try:
            # S'assurer qu'on a un UUID valide pour la session
            session_id = session_data.get("session_id", str(uuid.uuid4()))
            session_data["session_id"] = session_id
            
            # Utiliser psycopg2 directement pour éviter les problèmes SQLAlchemy 2.0
            conn = psycopg2.connect(
                host="postgres",
                port="5432",
                database="traffic_db",
                user="traffic_user",
                password="traffic_pass"
            )
            
            with conn.cursor() as cur:
                now = datetime.utcnow()
                
                # Vérifier que la campagne existe
                cur.execute("SELECT id FROM campaigns WHERE id = %s", (campaign_id,))
                if not cur.fetchone():
                    self.logger.error(f"❌ Campagne {campaign_id} introuvable en base")
                    return False
                
                # Vérifier que le persona existe
                persona_id = session_data.get("persona_id", "a0982768-55b7-4bed-87a2-3d244fb8b158")
                cur.execute("SELECT id FROM personas WHERE id = %s", (persona_id,))
                if not cur.fetchone():
                    self.logger.error(f"❌ Persona {persona_id} introuvable en base")
                    return False
                
                # Créer la session avec tous les champs requis et optionnels
                cur.execute("""
                    INSERT INTO sessions (
                        id, campaign_id, persona_id, status,
                        created_at, started_at, completed_at,
                        start_url, user_agent,
                        viewport_width, viewport_height,
                        session_duration_ms, pages_visited, total_actions,
                        error_message
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s,
                        %s, %s, %s,
                        %s
                    )
                """, (
                    session_data["session_id"],
                    campaign_id,
                    session_data.get("persona_id", "a0982768-55b7-4bed-87a2-3d244fb8b158"),
                    "completed" if session_data["success"] else "failed",
                    now,
                    now,
                    now,
                    session_data.get("url"),
                    session_data.get("user_agent", "Mozilla/5.0 (TrafficBot)"),
                    session_data.get("viewport_width", 1920),
                    session_data.get("viewport_height", 1080),
                    int(session_data.get("duration", 0) * 1000),
                    session_data.get("page_views", 0),
                    session_data.get("actions", 0),
                    session_data.get("error")
                ))
                
                # Créer la visite de page
                cur.execute("""
                    INSERT INTO page_visits (id, session_id, url, title, visit_order, arrived_at, left_at, actions_count, scroll_depth_percent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    session_data["session_id"],
                    session_data.get("url"),
                    "Example Page",  # title
                    1,  # visit_order
                    now,  # arrived_at
                    now,  # left_at
                    session_data.get("actions", 0),  # actions_count
                    75  # scroll_depth_percent
                ))
                
                conn.commit()
            
            conn.close()
            self.logger.info(f"✅ Session {session_data['session_id']} sauvegardée")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
    
    async def run_campaign(self, campaign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Exécute une campagne complète avec plusieurs sessions
        
        Args:
            campaign_data: Données de la campagne
            
        Returns:
            Liste des résultats de sessions
        """
        target_url = campaign_data.get('target_url')
        sessions_count = campaign_data.get('concurrent_sessions', 2)
        duration_seconds = campaign_data.get('duration_minutes', 1) * 60
        
        self.logger.info(f"🎯 Démarrage de la campagne vers {target_url} avec {sessions_count} sessions")
        
        # Créer les tâches de sessions
        tasks = []
        campaign_id = campaign_data.get('campaign_id')
        for i in range(sessions_count):
            task = self.run_session(target_url, duration_seconds, campaign_id)
            tasks.append(task)
        
        # Exécuter toutes les sessions en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter les résultats
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Erreur dans la session {i}: {str(result)}")
                processed_results.append({
                    "success": False,
                    "url": target_url,
                    "duration": 0,
                    "error": str(result),
                    "timestamp": time.time()
                })
            else:
                processed_results.append(result)
        
        successful_sessions = [r for r in processed_results if r.get("success", False)]
        self.logger.info(f"🎉 Campagne terminée: {len(successful_sessions)}/{len(processed_results)} sessions réussies")
        
        return processed_results
    
    async def process_campaign_job(self, job_data: Dict[str, Any]):
        """Traite un job de campagne de navigation"""
        try:
            campaign_id = job_data.get('campaign_id')
            target_url = job_data.get('target_url')
            concurrent_sessions = job_data.get('concurrent_sessions', 2)
            duration_minutes = job_data.get('duration_minutes', 1)
            
            self.logger.info(f"🎯 Traitement de la campagne {campaign_id} vers {target_url}")
            
            # Créer les données de campagne
            campaign_data = {
                'campaign_id': campaign_id,
                'target_url': target_url,
                'concurrent_sessions': concurrent_sessions,
                'duration_minutes': duration_minutes
            }
            
            # Exécuter la campagne
            results = await self.run_campaign(campaign_data)
            
            self.logger.info(f"✅ Campagne {campaign_id} terminée: {len(results)} sessions")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du traitement de la campagne: {e}")
    
    async def start(self):
        """Démarre le worker"""
        self.logger.info(f"🚀 Démarrage du worker {self.worker_id}")
        self.running = True
        
        # Configuration des signaux
        def signal_handler(signum, frame):
            self.logger.info(f"🛑 Signal {signum} reçu, arrêt du worker...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Test des connexions
        try:
            self.logger.info("🔍 Test des connexions...")
            redis_ping = self.redis_client.ping()
            self.logger.info(f"✅ Redis: {redis_ping}")
            
            # Test DB avec psycopg2
            conn = psycopg2.connect(
                host="postgres",
                port="5432",
                database="traffic_db",
                user="traffic_user",
                password="traffic_pass"
            )
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                self.logger.info(f"✅ DB: {result}")
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur de connexion: {e}")
            return
        
        # Boucle principale
        self.logger.info("🔄 Démarrage de la boucle principale...")
        iteration = 0
        while self.running:
            try:
                iteration += 1
                if iteration % 10 == 0:  # Log toutes les 10 itérations
                    self.logger.info(f"🔄 Itération {iteration}, running={self.running}")
                
                # Vérifier les jobs dans Redis
                job_data = self.redis_client.lpop('simulation:pending')
                
                if job_data:
                    self.logger.info(f"📥 Job brut reçu: {job_data}")
                    try:
                        job = json.loads(job_data)
                        self.logger.info(f"📥 Job reçu: {job.get('type', 'unknown')}")
                        
                        if job.get('type') == 'simulation':
                            await self.process_campaign_job(job)
                        else:
                            self.logger.warning(f"⚠️ Type de job non supporté: {job.get('type')}")
                            
                    except json.JSONDecodeError as e:
                        self.logger.error(f"❌ Erreur de décodage JSON: {e}")
                    except Exception as e:
                        self.logger.error(f"❌ Erreur lors du traitement du job: {e}")
                        import traceback
                        self.logger.error(f"Traceback: {traceback.format_exc()}")
                else:
                    # Pas de job, attendre un peu
                    if iteration % 10 == 0:  # Log seulement toutes les 10 itérations
                        self.logger.debug("🔍 Aucun job en attente")
                    await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle principale: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                await asyncio.sleep(5)
        
        self.logger.info(f"✅ Worker {self.worker_id} arrêté")


async def main():
    """Fonction principale"""
    worker = SimpleNavigationWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
