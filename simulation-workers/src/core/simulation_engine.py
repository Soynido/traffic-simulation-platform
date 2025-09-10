"""
Moteur de simulation principal pour la Traffic Simulation Platform.
Gère l'exécution des simulations de trafic web avec des comportements humains réalistes.
"""
import asyncio
import random
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Persona, Campaign, Session, PageVisit, Action
from ..services import SessionService, AnalyticsService
from ..utils.behavior_patterns import BehaviorPatterns
from ..utils.user_agents import UserAgentRotator
from ..utils.rhythm_calculator import RhythmCalculator


class SimulationStatus(Enum):
    """Statuts possibles d'une simulation."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SimulationConfig:
    """Configuration d'une simulation."""
    campaign_id: str
    persona_id: str
    target_url: str
    max_pages: int
    max_actions_per_page: int
    session_duration_min: int
    session_duration_max: int
    scroll_probability: float
    click_probability: float
    typing_probability: float
    rate_limit_delay_ms: int
    user_agent_rotation: bool
    respect_robots_txt: bool


@dataclass
class SimulationResult:
    """Résultat d'une simulation."""
    session_id: str
    status: SimulationStatus
    pages_visited: int
    actions_performed: int
    total_duration: float
    rhythm_score: float
    detection_risk: float
    error_message: Optional[str] = None


class SimulationEngine:
    """Moteur de simulation principal."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.session_service = SessionService(db_session)
        self.analytics_service = AnalyticsService(db_session)
        self.behavior_patterns = BehaviorPatterns()
        self.user_agent_rotator = UserAgentRotator()
        self.rhythm_calculator = RhythmCalculator()
        self.logger = logging.getLogger(__name__)
        
        # État de la simulation
        self.running_simulations: Dict[str, asyncio.Task] = {}
        self.simulation_configs: Dict[str, SimulationConfig] = {}
        
    async def start_simulation(self, config: SimulationConfig) -> str:
        """Démarrer une nouvelle simulation."""
        try:
            # Créer une session en base
            session_data = {
                'campaign_id': config.campaign_id,
                'persona_id': config.persona_id,
                'start_url': config.target_url,
                'user_agent': self.user_agent_rotator.get_random_user_agent() if config.user_agent_rotation else None,
                'viewport_width': random.randint(1200, 1920),
                'viewport_height': random.randint(800, 1080)
            }
            
            session = await self.session_service.create_session(session_data)
            session_id = str(session.id)
            
            # Stocker la configuration
            self.simulation_configs[session_id] = config
            
            # Démarrer la tâche de simulation
            task = asyncio.create_task(self._run_simulation(session_id, config))
            self.running_simulations[session_id] = task
            
            self.logger.info(f"Simulation démarrée: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage de la simulation: {e}")
            raise
    
    async def pause_simulation(self, session_id: str) -> bool:
        """Mettre en pause une simulation."""
        if session_id in self.running_simulations:
            task = self.running_simulations[session_id]
            task.cancel()
            del self.running_simulations[session_id]
            
            # Mettre à jour le statut en base
            await self.session_service.update_session_status(session_id, SimulationStatus.PAUSED.value)
            
            self.logger.info(f"Simulation mise en pause: {session_id}")
            return True
        return False
    
    async def resume_simulation(self, session_id: str) -> bool:
        """Reprendre une simulation en pause."""
        if session_id in self.simulation_configs:
            config = self.simulation_configs[session_id]
            task = asyncio.create_task(self._run_simulation(session_id, config))
            self.running_simulations[session_id] = task
            
            # Mettre à jour le statut en base
            await self.session_service.update_session_status(session_id, SimulationStatus.RUNNING.value)
            
            self.logger.info(f"Simulation reprise: {session_id}")
            return True
        return False
    
    async def stop_simulation(self, session_id: str) -> bool:
        """Arrêter définitivement une simulation."""
        if session_id in self.running_simulations:
            task = self.running_simulations[session_id]
            task.cancel()
            del self.running_simulations[session_id]
            
            # Mettre à jour le statut en base
            await self.session_service.update_session_status(session_id, SimulationStatus.COMPLETED.value)
            
            self.logger.info(f"Simulation arrêtée: {session_id}")
            return True
        return False
    
    async def _run_simulation(self, session_id: str, config: SimulationConfig) -> SimulationResult:
        """Exécuter une simulation complète."""
        start_time = time.time()
        pages_visited = 0
        actions_performed = 0
        rhythm_events = []
        
        try:
            # Mettre à jour le statut
            await self.session_service.update_session_status(session_id, SimulationStatus.RUNNING.value)
            
            # Démarrer Playwright
            async with async_playwright() as p:
                # Choisir le navigateur
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                # Créer le contexte
                context = await browser.new_context(
                    user_agent=config.user_agent_rotation and self.user_agent_rotator.get_random_user_agent(),
                    viewport={'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)}
                )
                
                # Créer la page
                page = await context.new_page()
                
                # Configurer les timeouts
                page.set_default_timeout(30000)
                page.set_default_navigation_timeout(30000)
                
                # Démarrer la simulation
                current_url = config.target_url
                max_pages = random.randint(config.max_pages // 2, config.max_pages)
                session_duration = random.randint(config.session_duration_min, config.session_duration_max)
                
                while pages_visited < max_pages and (time.time() - start_time) < session_duration:
                    try:
                        # Visiter la page
                        await self._visit_page(page, current_url, session_id, pages_visited)
                        pages_visited += 1
                        
                        # Effectuer des actions sur la page
                        page_actions = await self._perform_page_actions(
                            page, session_id, pages_visited, config, rhythm_events
                        )
                        actions_performed += page_actions
                        
                        # Délai entre les pages
                        await asyncio.sleep(random.uniform(1.0, 3.0))
                        
                        # Naviguer vers une nouvelle page (si possible)
                        current_url = await self._navigate_to_next_page(page, current_url)
                        
                    except Exception as e:
                        self.logger.warning(f"Erreur lors de la visite de la page {pages_visited}: {e}")
                        break
                
                # Fermer le navigateur
                await browser.close()
            
            # Calculer les métriques finales
            total_duration = time.time() - start_time
            rhythm_score = self.rhythm_calculator.calculate_rhythm_score(rhythm_events)
            detection_risk = self.rhythm_calculator.calculate_detection_risk(rhythm_events)
            
            # Mettre à jour la session
            await self.session_service.update_session_completion(
                session_id, 
                pages_visited, 
                actions_performed, 
                total_duration
            )
            
            # Créer le résultat
            result = SimulationResult(
                session_id=session_id,
                status=SimulationStatus.COMPLETED,
                pages_visited=pages_visited,
                actions_performed=actions_performed,
                total_duration=total_duration,
                rhythm_score=rhythm_score,
                detection_risk=detection_risk
            )
            
            self.logger.info(f"Simulation terminée: {session_id} - {pages_visited} pages, {actions_performed} actions")
            return result
            
        except asyncio.CancelledError:
            # Simulation annulée
            await self.session_service.update_session_status(session_id, SimulationStatus.PAUSED.value)
            raise
            
        except Exception as e:
            # Erreur lors de la simulation
            self.logger.error(f"Erreur lors de la simulation {session_id}: {e}")
            await self.session_service.update_session_status(session_id, SimulationStatus.FAILED.value)
            
            return SimulationResult(
                session_id=session_id,
                status=SimulationStatus.FAILED,
                pages_visited=pages_visited,
                actions_performed=actions_performed,
                total_duration=time.time() - start_time,
                rhythm_score=0.0,
                detection_risk=1.0,
                error_message=str(e)
            )
    
    async def _visit_page(self, page: Page, url: str, session_id: str, page_number: int) -> None:
        """Visiter une page et enregistrer la visite."""
        try:
            # Naviguer vers la page
            response = await page.goto(url, wait_until='domcontentloaded')
            
            # Attendre que la page soit chargée
            await page.wait_for_load_state('networkidle')
            
            # Enregistrer la visite en base
            visit_data = {
                'session_id': session_id,
                'url': url,
                'page_number': page_number,
                'load_time': response.timing['loadEventEnd'] - response.timing['loadEventStart'] if response.timing else 0,
                'title': await page.title(),
                'viewport_width': page.viewport_size['width'],
                'viewport_height': page.viewport_size['height']
            }
            
            await self.session_service.create_page_visit(visit_data)
            
        except Exception as e:
            self.logger.warning(f"Erreur lors de la visite de {url}: {e}")
            raise
    
    async def _perform_page_actions(
        self, 
        page: Page, 
        session_id: str, 
        page_number: int, 
        config: SimulationConfig,
        rhythm_events: List[Dict[str, Any]]
    ) -> int:
        """Effectuer des actions sur la page actuelle."""
        actions_count = 0
        max_actions = random.randint(config.max_actions_per_page // 2, config.max_actions_per_page)
        
        try:
            # Attendre que la page soit interactive
            await page.wait_for_load_state('domcontentloaded')
            
            # Actions de scroll
            if random.random() < config.scroll_probability:
                await self._perform_scroll_actions(page, session_id, page_number, rhythm_events)
                actions_count += 1
            
            # Actions de clic
            if random.random() < config.click_probability:
                await self._perform_click_actions(page, session_id, page_number, rhythm_events)
                actions_count += 1
            
            # Actions de frappe
            if random.random() < config.typing_probability:
                await self._perform_typing_actions(page, session_id, page_number, rhythm_events)
                actions_count += 1
            
            # Délai entre les actions
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            self.logger.warning(f"Erreur lors des actions sur la page {page_number}: {e}")
        
        return actions_count
    
    async def _perform_scroll_actions(
        self, 
        page: Page, 
        session_id: str, 
        page_number: int,
        rhythm_events: List[Dict[str, Any]]
    ) -> None:
        """Effectuer des actions de scroll réalistes."""
        try:
            # Obtenir la hauteur de la page
            page_height = await page.evaluate("document.body.scrollHeight")
            viewport_height = page.viewport_size['height']
            
            # Calculer le nombre de scrolls
            scroll_count = random.randint(1, min(5, page_height // viewport_height))
            
            for i in range(scroll_count):
                # Scroll progressif
                scroll_position = (i + 1) * viewport_height * 0.8
                await page.evaluate(f"window.scrollTo(0, {scroll_position})")
                
                # Enregistrer l'action
                action_data = {
                    'session_id': session_id,
                    'page_number': page_number,
                    'action_type': 'scroll',
                    'timestamp': time.time(),
                    'details': {'position': scroll_position}
                }
                
                await self.session_service.create_action(action_data)
                
                # Enregistrer l'événement de rythme
                rhythm_events.append({
                    'type': 'scroll',
                    'timestamp': time.time(),
                    'position': scroll_position
                })
                
                # Délai entre les scrolls
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            self.logger.warning(f"Erreur lors du scroll: {e}")
    
    async def _perform_click_actions(
        self, 
        page: Page, 
        session_id: str, 
        page_number: int,
        rhythm_events: List[Dict[str, Any]]
    ) -> None:
        """Effectuer des actions de clic réalistes."""
        try:
            # Trouver des éléments cliquables
            clickable_elements = await page.query_selector_all('a, button, input[type="submit"], input[type="button"]')
            
            if clickable_elements:
                # Choisir un élément aléatoire
                element = random.choice(clickable_elements)
                
                # Vérifier que l'élément est visible
                is_visible = await element.is_visible()
                if is_visible:
                    # Cliquer sur l'élément
                    await element.click()
                    
                    # Enregistrer l'action
                    action_data = {
                        'session_id': session_id,
                        'page_number': page_number,
                        'action_type': 'click',
                        'timestamp': time.time(),
                        'details': {'element': await element.get_attribute('tagName')}
                    }
                    
                    await self.session_service.create_action(action_data)
                    
                    # Enregistrer l'événement de rythme
                    rhythm_events.append({
                        'type': 'click',
                        'timestamp': time.time(),
                        'element': await element.get_attribute('tagName')
                    })
                    
                    # Attendre la navigation si c'est un lien
                    if await element.get_attribute('tagName') == 'A':
                        await page.wait_for_load_state('domcontentloaded')
                
        except Exception as e:
            self.logger.warning(f"Erreur lors du clic: {e}")
    
    async def _perform_typing_actions(
        self, 
        page: Page, 
        session_id: str, 
        page_number: int,
        rhythm_events: List[Dict[str, Any]]
    ) -> None:
        """Effectuer des actions de frappe réalistes."""
        try:
            # Trouver des champs de saisie
            input_elements = await page.query_selector_all('input[type="text"], input[type="email"], textarea')
            
            if input_elements:
                # Choisir un élément aléatoire
                element = random.choice(input_elements)
                
                # Vérifier que l'élément est visible et éditable
                is_visible = await element.is_visible()
                is_editable = await element.is_editable()
                
                if is_visible and is_editable:
                    # Focus sur l'élément
                    await element.focus()
                    
                    # Générer du texte réaliste
                    text = self.behavior_patterns.generate_realistic_text()
                    
                    # Frapper le texte avec des délais réalistes
                    await element.type(text, delay=random.randint(50, 150))
                    
                    # Enregistrer l'action
                    action_data = {
                        'session_id': session_id,
                        'page_number': page_number,
                        'action_type': 'typing',
                        'timestamp': time.time(),
                        'details': {'text_length': len(text)}
                    }
                    
                    await self.session_service.create_action(action_data)
                    
                    # Enregistrer l'événement de rythme
                    rhythm_events.append({
                        'type': 'typing',
                        'timestamp': time.time(),
                        'text_length': len(text)
                    })
                
        except Exception as e:
            self.logger.warning(f"Erreur lors de la frappe: {e}")
    
    async def _navigate_to_next_page(self, page: Page, current_url: str) -> str:
        """Naviguer vers une nouvelle page."""
        try:
            # Trouver des liens sur la page
            links = await page.query_selector_all('a[href]')
            
            if links:
                # Choisir un lien aléatoire
                link = random.choice(links)
                href = await link.get_attribute('href')
                
                if href and href.startswith('http'):
                    return href
                elif href and href.startswith('/'):
                    # Lien relatif
                    from urllib.parse import urljoin
                    return urljoin(current_url, href)
            
            # Si aucun lien trouvé, rester sur la page actuelle
            return current_url
            
        except Exception as e:
            self.logger.warning(f"Erreur lors de la navigation: {e}")
            return current_url
    
    async def get_simulation_status(self, session_id: str) -> Optional[SimulationStatus]:
        """Obtenir le statut d'une simulation."""
        if session_id in self.running_simulations:
            return SimulationStatus.RUNNING
        elif session_id in self.simulation_configs:
            return SimulationStatus.PAUSED
        else:
            # Vérifier en base de données
            session = await self.session_service.get_session(session_id)
            if session:
                return SimulationStatus(session.status)
            return None
    
    async def get_running_simulations(self) -> List[str]:
        """Obtenir la liste des simulations en cours."""
        return list(self.running_simulations.keys())
    
    async def cleanup_completed_simulations(self) -> None:
        """Nettoyer les simulations terminées."""
        completed_sessions = []
        
        for session_id, task in self.running_simulations.items():
            if task.done():
                completed_sessions.append(session_id)
        
        for session_id in completed_sessions:
            del self.running_simulations[session_id]
            if session_id in self.simulation_configs:
                del self.simulation_configs[session_id]
        
        if completed_sessions:
            self.logger.info(f"Simulations terminées nettoyées: {len(completed_sessions)}")
