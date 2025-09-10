"""
Gestionnaire de rotation des user agents pour la simulation de trafic.
Fournit des user agents réalistes et variés.
"""
import random
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class UserAgentInfo:
    """Informations sur un user agent."""
    user_agent: str
    browser: str
    version: str
    os: str
    device_type: str
    market_share: float


class UserAgentRotator:
    """Gestionnaire de rotation des user agents."""
    
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.used_agents = set()
        self.agent_weights = self._calculate_weights()
    
    def _load_user_agents(self) -> List[UserAgentInfo]:
        """Charge la liste des user agents réalistes."""
        return [
            # Chrome sur Windows
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                os="Windows 10",
                device_type="desktop",
                market_share=0.35
            ),
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                browser="Chrome",
                version="119.0.0.0",
                os="Windows 10",
                device_type="desktop",
                market_share=0.25
            ),
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                os="Windows 11",
                device_type="desktop",
                market_share=0.15
            ),
            
            # Chrome sur macOS
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                os="macOS 10.15",
                device_type="desktop",
                market_share=0.08
            ),
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                os="macOS 13",
                device_type="desktop",
                market_share=0.05
            ),
            
            # Chrome sur Linux
            UserAgentInfo(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                os="Linux",
                device_type="desktop",
                market_share=0.03
            ),
            
            # Firefox sur Windows
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                browser="Firefox",
                version="121.0",
                os="Windows 10",
                device_type="desktop",
                market_share=0.08
            ),
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                browser="Firefox",
                version="120.0",
                os="Windows 10",
                device_type="desktop",
                market_share=0.05
            ),
            
            # Firefox sur macOS
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                browser="Firefox",
                version="121.0",
                os="macOS 10.15",
                device_type="desktop",
                market_share=0.03
            ),
            
            # Safari sur macOS
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                browser="Safari",
                version="17.1",
                os="macOS 10.15",
                device_type="desktop",
                market_share=0.08
            ),
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                browser="Safari",
                version="17.1",
                os="macOS 13",
                device_type="desktop",
                market_share=0.05
            ),
            
            # Edge sur Windows
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                browser="Edge",
                version="120.0.0.0",
                os="Windows 10",
                device_type="desktop",
                market_share=0.06
            ),
            
            # Chrome Mobile
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                browser="Chrome Mobile",
                version="120.0.0.0",
                os="Android 10",
                device_type="mobile",
                market_share=0.12
            ),
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                browser="Chrome Mobile",
                version="120.0.0.0",
                os="Android 11",
                device_type="mobile",
                market_share=0.08
            ),
            
            # Safari Mobile
            UserAgentInfo(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                browser="Safari Mobile",
                version="17.1",
                os="iOS 17.1",
                device_type="mobile",
                market_share=0.15
            ),
            UserAgentInfo(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                browser="Safari Mobile",
                version="16.6",
                os="iOS 16.6",
                device_type="mobile",
                market_share=0.10
            ),
            
            # Chrome sur iPad
            UserAgentInfo(
                user_agent="Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
                browser="Chrome Mobile",
                version="120.0.6099.119",
                os="iPadOS 17.1",
                device_type="tablet",
                market_share=0.05
            ),
            
            # Firefox Mobile
            UserAgentInfo(
                user_agent="Mozilla/5.0 (Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
                browser="Firefox Mobile",
                version="121.0",
                os="Android",
                device_type="mobile",
                market_share=0.02
            ),
        ]
    
    def _calculate_weights(self) -> List[float]:
        """Calcule les poids pour la sélection pondérée des user agents."""
        total_share = sum(agent.market_share for agent in self.user_agents)
        return [agent.market_share / total_share for agent in self.user_agents]
    
    def get_random_user_agent(self) -> str:
        """Sélectionne un user agent aléatoire basé sur les parts de marché."""
        # Utiliser la sélection pondérée
        selected_agent = random.choices(
            self.user_agents,
            weights=self.agent_weights,
            k=1
        )[0]
        
        return selected_agent.user_agent
    
    def get_user_agent_by_browser(self, browser: str) -> str:
        """Sélectionne un user agent pour un navigateur spécifique."""
        browser_agents = [agent for agent in self.user_agents if agent.browser.lower() == browser.lower()]
        
        if not browser_agents:
            return self.get_random_user_agent()
        
        # Calculer les poids pour ce navigateur
        total_share = sum(agent.market_share for agent in browser_agents)
        weights = [agent.market_share / total_share for agent in browser_agents]
        
        selected_agent = random.choices(browser_agents, weights=weights, k=1)[0]
        return selected_agent.user_agent
    
    def get_user_agent_by_os(self, os: str) -> str:
        """Sélectionne un user agent pour un système d'exploitation spécifique."""
        os_agents = [agent for agent in self.user_agents if os.lower() in agent.os.lower()]
        
        if not os_agents:
            return self.get_random_user_agent()
        
        # Calculer les poids pour cet OS
        total_share = sum(agent.market_share for agent in os_agents)
        weights = [agent.market_share / total_share for agent in os_agents]
        
        selected_agent = random.choices(os_agents, weights=weights, k=1)[0]
        return selected_agent.user_agent
    
    def get_user_agent_by_device_type(self, device_type: str) -> str:
        """Sélectionne un user agent pour un type d'appareil spécifique."""
        device_agents = [agent for agent in self.user_agents if agent.device_type.lower() == device_type.lower()]
        
        if not device_agents:
            return self.get_random_user_agent()
        
        # Calculer les poids pour ce type d'appareil
        total_share = sum(agent.market_share for agent in device_agents)
        weights = [agent.market_share / total_share for agent in device_agents]
        
        selected_agent = random.choices(device_agents, weights=weights, k=1)[0]
        return selected_agent.user_agent
    
    def get_user_agent_info(self, user_agent: str) -> UserAgentInfo:
        """Obtient les informations détaillées d'un user agent."""
        for agent in self.user_agents:
            if agent.user_agent == user_agent:
                return agent
        
        # Si non trouvé, retourner un agent par défaut
        return self.user_agents[0]
    
    def get_browser_distribution(self) -> Dict[str, float]:
        """Obtient la distribution des navigateurs."""
        distribution = {}
        for agent in self.user_agents:
            browser = agent.browser
            if browser in distribution:
                distribution[browser] += agent.market_share
            else:
                distribution[browser] = agent.market_share
        
        return distribution
    
    def get_os_distribution(self) -> Dict[str, float]:
        """Obtient la distribution des systèmes d'exploitation."""
        distribution = {}
        for agent in self.user_agents:
            os = agent.os
            if os in distribution:
                distribution[os] += agent.market_share
            else:
                distribution[os] = agent.market_share
        
        return distribution
    
    def get_device_type_distribution(self) -> Dict[str, float]:
        """Obtient la distribution des types d'appareils."""
        distribution = {}
        for agent in self.user_agents:
            device_type = agent.device_type
            if device_type in distribution:
                distribution[device_type] += agent.market_share
            else:
                distribution[device_type] = agent.market_share
        
        return distribution
    
    def get_realistic_user_agent_sequence(self, count: int) -> List[str]:
        """Génère une séquence réaliste de user agents."""
        sequence = []
        
        # Mélanger les user agents pour éviter la répétition
        shuffled_agents = self.user_agents.copy()
        random.shuffle(shuffled_agents)
        
        for i in range(count):
            # Sélectionner un agent en évitant les répétitions récentes
            available_agents = [agent for agent in shuffled_agents if agent.user_agent not in sequence[-5:]]
            
            if available_agents:
                selected_agent = random.choices(
                    available_agents,
                    weights=[agent.market_share for agent in available_agents],
                    k=1
                )[0]
            else:
                selected_agent = random.choice(shuffled_agents)
            
            sequence.append(selected_agent.user_agent)
        
        return sequence
    
    def validate_user_agent(self, user_agent: str) -> bool:
        """Valide qu'un user agent est dans la liste des agents supportés."""
        return any(agent.user_agent == user_agent for agent in self.user_agents)
    
    def get_user_agent_statistics(self) -> Dict[str, Any]:
        """Obtient des statistiques sur les user agents."""
        total_agents = len(self.user_agents)
        browsers = set(agent.browser for agent in self.user_agents)
        operating_systems = set(agent.os for agent in self.user_agents)
        device_types = set(agent.device_type for agent in self.user_agents)
        
        return {
            'total_agents': total_agents,
            'unique_browsers': len(browsers),
            'unique_operating_systems': len(operating_systems),
            'unique_device_types': len(device_types),
            'browser_distribution': self.get_browser_distribution(),
            'os_distribution': self.get_os_distribution(),
            'device_type_distribution': self.get_device_type_distribution()
        }
