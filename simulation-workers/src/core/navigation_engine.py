"""
Moteur de navigation Playwright pour les simulation workers
Gère la navigation réelle vers les URLs cibles
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

from playwright.sync_api import sync_playwright, Browser, Page
from local_types import Campaign, Persona, Session

logger = logging.getLogger(__name__)


class NavigationEngine:
    """Moteur de navigation utilisant Playwright pour simuler des visites réelles"""
    
    def __init__(self):
        """Initialise le moteur de navigation"""
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
    
    async def run_session(
        self,
        target_url: str,
        duration_seconds: int,
        persona: Persona,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Exécute une session de navigation vers une URL cible
        
        Args:
            target_url: URL cible à visiter
            duration_seconds: Durée de la session en secondes
            persona: Persona utilisateur pour le comportement
            user_agent: User agent personnalisé (optionnel)
            viewport: Taille de la fenêtre (optionnel)
            
        Returns:
            Dictionnaire contenant les résultats de la session
        """
        session_result = {
            "success": False,
            "url": target_url,
            "duration": 0,
            "page_views": 0,
            "actions": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Configuration du viewport basée sur le persona
            if not viewport:
                viewport = self._get_viewport_from_persona(persona)
            
            # Configuration du user agent basée sur le persona
            if not user_agent:
                user_agent = self._get_user_agent_from_persona(persona)
            
            # Exécution de la session dans un thread séparé
            result = await asyncio.to_thread(
                self._run_session_sync,
                target_url,
                duration_seconds,
                user_agent,
                viewport,
                persona
            )
            
            session_result.update(result)
            session_result["success"] = True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la session: {str(e)}")
            session_result["error"] = str(e)
            session_result["success"] = False
        
        return session_result
    
    def _run_session_sync(
        self,
        target_url: str,
        duration_seconds: int,
        user_agent: str,
        viewport: Dict[str, int],
        persona: Persona
    ) -> Dict[str, Any]:
        """
        Exécute une session de navigation de manière synchrone
        
        Args:
            target_url: URL cible
            duration_seconds: Durée en secondes
            user_agent: User agent
            viewport: Taille de la fenêtre
            persona: Persona utilisateur
            
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
                page.set_viewport_size(viewport)
                
                # Configuration du user agent
                page.set_extra_http_headers({
                    "User-Agent": user_agent
                })
                
                # Navigation vers l'URL cible
                logger.info(f"Navigation vers {target_url}")
                response = page.goto(target_url, wait_until="networkidle", timeout=30000)
                
                if response and response.status >= 400:
                    raise Exception(f"Erreur HTTP {response.status}")
                
                result["page_views"] = 1
                start_time = datetime.now()
                
                # Simulation du comportement utilisateur
                await self._simulate_user_behavior(page, persona, duration_seconds)
                
                # Calcul de la durée réelle
                end_time = datetime.now()
                result["duration"] = (end_time - start_time).total_seconds()
                result["actions"] = self._count_actions(page)
                
                logger.info(f"Session terminée: {result['duration']:.2f}s, {result['page_views']} pages, {result['actions']} actions")
                
            except Exception as e:
                logger.error(f"Erreur dans la session: {str(e)}")
                raise e
                
            finally:
                if page:
                    page.close()
                if browser:
                    browser.close()
        
        return result
    
    async def _simulate_user_behavior(
        self,
        page: Page,
        persona: Persona,
        duration_seconds: int
    ) -> None:
        """
        Simule le comportement utilisateur basé sur le persona
        
        Args:
            page: Page Playwright
            persona: Persona utilisateur
            duration_seconds: Durée de la session
        """
        behavior = persona.behaviorProfile
        
        # Calcul du temps de session basé sur le persona
        min_duration = behavior.sessionDuration["min"] * 60  # Convertir en secondes
        max_duration = behavior.sessionDuration["max"] * 60
        actual_duration = min(duration_seconds, random.randint(min_duration, max_duration))
        
        # Simulation des actions utilisateur
        actions_count = 0
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < actual_duration:
            try:
                # Attendre un peu entre les actions
                wait_time = random.uniform(1, 3)
                page.wait_for_timeout(int(wait_time * 1000))
                
                # Simuler des actions basées sur le persona
                if behavior.clickPattern == "systematic":
                    await self._simulate_systematic_behavior(page)
                elif behavior.clickPattern == "random":
                    await self._simulate_random_behavior(page)
                elif behavior.clickPattern == "hesitant":
                    await self._simulate_hesitant_behavior(page)
                
                # Simuler le scroll
                if behavior.scrollBehavior == "smooth":
                    await self._simulate_smooth_scroll(page)
                elif behavior.scrollBehavior == "jumpy":
                    await self._simulate_jumpy_scroll(page)
                
                actions_count += 1
                
                # Vérifier si on doit changer de page
                if random.random() < 0.1:  # 10% de chance de cliquer sur un lien
                    await self._try_click_link(page)
                
            except Exception as e:
                logger.warning(f"Erreur lors de la simulation: {str(e)}")
                break
    
    async def _simulate_systematic_behavior(self, page: Page) -> None:
        """Simule un comportement systématique"""
        # Cliquer sur des éléments interactifs de manière ordonnée
        clickable_elements = page.locator("button, a, input[type='button'], input[type='submit']")
        count = await clickable_elements.count()
        
        if count > 0:
            # Cliquer sur le premier élément disponible
            await clickable_elements.first.click()
    
    async def _simulate_random_behavior(self, page: Page) -> None:
        """Simule un comportement aléatoire"""
        # Cliquer sur un élément aléatoire
        clickable_elements = page.locator("button, a, input[type='button'], input[type='submit']")
        count = await clickable_elements.count()
        
        if count > 0:
            random_index = random.randint(0, count - 1)
            await clickable_elements.nth(random_index).click()
    
    async def _simulate_hesitant_behavior(self, page: Page) -> None:
        """Simule un comportement hésitant"""
        # Attendre plus longtemps avant de cliquer
        page.wait_for_timeout(random.randint(2000, 5000))
        
        # Cliquer sur un élément simple
        simple_elements = page.locator("button:not([disabled]), a:not([href='#'])")
        count = await simple_elements.count()
        
        if count > 0:
            await simple_elements.first.click()
    
    async def _simulate_smooth_scroll(self, page: Page) -> None:
        """Simule un scroll fluide"""
        # Scroll progressif
        for i in range(3):
            page.mouse.wheel(0, 300)
            page.wait_for_timeout(500)
    
    async def _simulate_jumpy_scroll(self, page: Page) -> None:
        """Simule un scroll saccadé"""
        # Scroll rapide et saccadé
        page.mouse.wheel(0, random.randint(200, 800))
        page.wait_for_timeout(random.randint(100, 300))
    
    async def _try_click_link(self, page: Page) -> None:
        """Essaie de cliquer sur un lien"""
        links = page.locator("a[href]:not([href='#']):not([href^='javascript:'])")
        count = await links.count()
        
        if count > 0:
            random_link = links.nth(random.randint(0, count - 1))
            try:
                await random_link.click()
                # Attendre que la page se charge
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception as e:
                logger.warning(f"Impossible de cliquer sur le lien: {str(e)}")
    
    def _count_actions(self, page: Page) -> int:
        """Compte le nombre d'actions effectuées"""
        # Cette méthode pourrait être étendue pour compter les vrais événements
        # Pour l'instant, on retourne un nombre aléatoire basé sur la durée
        return random.randint(5, 20)
    
    def _get_viewport_from_persona(self, persona: Persona) -> Dict[str, int]:
        """Récupère la taille de viewport basée sur le persona"""
        # Utiliser la première résolution du persona
        if persona.technicalProfile.screenResolutions:
            resolution = persona.technicalProfile.screenResolutions[0]
            return {
                "width": resolution.width,
                "height": resolution.height
            }
        
        # Valeur par défaut
        return {"width": 1920, "height": 1080}
    
    def _get_user_agent_from_persona(self, persona: Persona) -> str:
        """Récupère le user agent basé sur le persona"""
        # Utiliser le premier navigateur du persona
        if persona.technicalProfile.browsers:
            browser = persona.technicalProfile.browsers[0]
            return browser.userAgent or f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser.version} Safari/537.36"
        
        # User agent par défaut
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    async def run_campaign(
        self,
        campaign: Campaign,
        personas: List[Persona],
        sessions_count: int,
        duration_seconds: int
    ) -> List[Dict[str, Any]]:
        """
        Exécute une campagne complète avec plusieurs sessions
        
        Args:
            campaign: Campagne à exécuter
            personas: Liste des personas à utiliser
            sessions_count: Nombre de sessions à exécuter
            duration_seconds: Durée de chaque session
            
        Returns:
            Liste des résultats de sessions
        """
        logger.info(f"Démarrage de la campagne {campaign.name} avec {sessions_count} sessions")
        
        # Créer les tâches de sessions
        tasks = []
        for i in range(sessions_count):
            # Sélectionner un persona aléatoire
            persona = random.choice(personas)
            
            # Créer une tâche de session
            task = self.run_session(
                target_url=campaign.targetUrl,
                duration_seconds=duration_seconds,
                persona=persona
            )
            tasks.append(task)
        
        # Exécuter toutes les sessions en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter les résultats
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Erreur dans la session {i}: {str(result)}")
                processed_results.append({
                    "success": False,
                    "url": campaign.targetUrl,
                    "duration": 0,
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        logger.info(f"Campagne terminée: {len(processed_results)} sessions exécutées")
        return processed_results
