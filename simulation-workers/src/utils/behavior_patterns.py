"""
Patterns de comportement humain pour la simulation de trafic.
Génère des comportements réalistes basés sur des données réelles.
"""
import random
import time
from typing import List, Dict, Any
import numpy as np


class BehaviorPatterns:
    """Générateur de patterns de comportement humain."""
    
    def __init__(self):
        # Patterns de frappe réalistes
        self.typing_patterns = {
            'fast': {'min_delay': 50, 'max_delay': 100, 'error_rate': 0.02},
            'normal': {'min_delay': 100, 'max_delay': 200, 'error_rate': 0.05},
            'slow': {'min_delay': 200, 'max_delay': 400, 'error_rate': 0.08}
        }
        
        # Patterns de scroll
        self.scroll_patterns = {
            'rapid': {'speed': 'fast', 'pause_probability': 0.1},
            'careful': {'speed': 'slow', 'pause_probability': 0.3},
            'social': {'speed': 'normal', 'pause_probability': 0.2}
        }
        
        # Patterns de clic
        self.click_patterns = {
            'aggressive': {'double_click_probability': 0.1, 'hover_time': 0.1},
            'careful': {'double_click_probability': 0.05, 'hover_time': 0.5},
            'social': {'double_click_probability': 0.15, 'hover_time': 0.2}
        }
        
        # Textes réalistes pour les formulaires
        self.realistic_texts = {
            'names': [
                'John Smith', 'Sarah Johnson', 'Mike Davis', 'Lisa Wilson',
                'David Brown', 'Emma Taylor', 'Chris Anderson', 'Amy Martinez',
                'James Garcia', 'Maria Rodriguez', 'Robert Lee', 'Jennifer White'
            ],
            'emails': [
                'john.smith@email.com', 'sarah.j@company.com', 'mike.davis123@gmail.com',
                'lisa.wilson@outlook.com', 'david.brown@yahoo.com', 'emma.taylor@hotmail.com'
            ],
            'companies': [
                'Acme Corp', 'Tech Solutions', 'Global Industries', 'Innovation Labs',
                'Digital Dynamics', 'Future Systems', 'Creative Works', 'Smart Solutions'
            ],
            'messages': [
                'This looks interesting, I would like to know more.',
                'Could you please send me additional information?',
                'I am interested in your services.',
                'This seems like a great opportunity.',
                'I would like to schedule a meeting.',
                'Please contact me for more details.'
            ]
        }
        
        # Patterns de navigation
        self.navigation_patterns = {
            'explorer': {'back_probability': 0.3, 'new_tab_probability': 0.2},
            'focused': {'back_probability': 0.1, 'new_tab_probability': 0.05},
            'social': {'back_probability': 0.2, 'new_tab_probability': 0.4}
        }
    
    def generate_realistic_text(self, text_type: str = 'message') -> str:
        """Génère du texte réaliste basé sur le type."""
        if text_type == 'name':
            return random.choice(self.realistic_texts['names'])
        elif text_type == 'email':
            return random.choice(self.realistic_texts['emails'])
        elif text_type == 'company':
            return random.choice(self.realistic_texts['companies'])
        else:
            return random.choice(self.realistic_texts['messages'])
    
    def get_typing_delay(self, pattern: str = 'normal') -> int:
        """Génère un délai de frappe réaliste."""
        config = self.typing_patterns.get(pattern, self.typing_patterns['normal'])
        base_delay = random.randint(config['min_delay'], config['max_delay'])
        
        # Ajouter des variations naturelles
        variation = random.gauss(0, base_delay * 0.1)
        delay = max(10, int(base_delay + variation))
        
        return delay
    
    def should_make_typing_error(self, pattern: str = 'normal') -> bool:
        """Détermine si une erreur de frappe doit être simulée."""
        config = self.typing_patterns.get(pattern, self.typing_patterns['normal'])
        return random.random() < config['error_rate']
    
    def get_scroll_behavior(self, pattern: str = 'normal') -> Dict[str, Any]:
        """Génère un comportement de scroll réaliste."""
        config = self.scroll_patterns.get(pattern, self.scroll_patterns['normal'])
        
        # Vitesse de scroll basée sur le pattern
        if config['speed'] == 'fast':
            scroll_amount = random.randint(200, 500)
            pause_duration = random.uniform(0.1, 0.3)
        elif config['speed'] == 'slow':
            scroll_amount = random.randint(50, 150)
            pause_duration = random.uniform(0.5, 1.0)
        else:  # normal
            scroll_amount = random.randint(100, 300)
            pause_duration = random.uniform(0.2, 0.6)
        
        return {
            'amount': scroll_amount,
            'pause_duration': pause_duration,
            'should_pause': random.random() < config['pause_probability']
        }
    
    def get_click_behavior(self, pattern: str = 'normal') -> Dict[str, Any]:
        """Génère un comportement de clic réaliste."""
        config = self.click_patterns.get(pattern, self.click_patterns['careful'])
        
        return {
            'double_click': random.random() < config['double_click_probability'],
            'hover_time': random.uniform(0.1, config['hover_time']),
            'click_delay': random.uniform(0.05, 0.2)
        }
    
    def get_navigation_behavior(self, pattern: str = 'focused') -> Dict[str, Any]:
        """Génère un comportement de navigation réaliste."""
        config = self.navigation_patterns.get(pattern, self.navigation_patterns['focused'])
        
        return {
            'back_probability': config['back_probability'],
            'new_tab_probability': config['new_tab_probability'],
            'time_on_page': random.uniform(5, 30)  # secondes
        }
    
    def generate_mouse_movement(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Dict[str, int]]:
        """Génère un mouvement de souris réaliste entre deux points."""
        # Utiliser une courbe de Bézier pour un mouvement naturel
        control_x = random.randint(min(start_x, end_x), max(start_x, end_x))
        control_y = random.randint(min(start_y, end_y), max(start_y, end_y))
        
        # Générer des points le long de la courbe
        points = []
        steps = random.randint(5, 15)
        
        for i in range(steps + 1):
            t = i / steps
            
            # Courbe de Bézier quadratique
            x = int((1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x)
            y = int((1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y)
            
            # Ajouter du bruit pour plus de réalisme
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
            
            points.append({'x': x, 'y': y})
        
        return points
    
    def get_reading_time(self, text_length: int, pattern: str = 'normal') -> float:
        """Calcule le temps de lecture réaliste pour un texte."""
        # Vitesse de lecture moyenne : 200-300 mots par minute
        words_per_minute = {
            'fast': 300,
            'normal': 250,
            'slow': 200
        }
        
        wpm = words_per_minute.get(pattern, words_per_minute['normal'])
        words = text_length / 5  # Estimation approximative
        reading_time = (words / wpm) * 60  # en secondes
        
        # Ajouter de la variation
        variation = random.gauss(0, reading_time * 0.2)
        return max(1.0, reading_time + variation)
    
    def get_attention_span(self, pattern: str = 'normal') -> float:
        """Génère une durée d'attention réaliste."""
        attention_spans = {
            'short': (5, 15),    # 5-15 secondes
            'normal': (15, 45),  # 15-45 secondes
            'long': (45, 120)    # 45-120 secondes
        }
        
        min_time, max_time = attention_spans.get(pattern, attention_spans['normal'])
        return random.uniform(min_time, max_time)
    
    def should_abandon_session(self, time_on_page: float, pattern: str = 'normal') -> bool:
        """Détermine si l'utilisateur devrait abandonner la session."""
        abandonment_rates = {
            'impatient': 0.3,   # 30% de chance d'abandon
            'normal': 0.1,      # 10% de chance d'abandon
            'patient': 0.05     # 5% de chance d'abandon
        }
        
        base_rate = abandonment_rates.get(pattern, abandonment_rates['normal'])
        
        # Augmenter la probabilité avec le temps
        time_factor = min(1.0, time_on_page / 60)  # Max après 1 minute
        adjusted_rate = base_rate * (1 + time_factor)
        
        return random.random() < adjusted_rate
    
    def get_form_filling_behavior(self, pattern: str = 'normal') -> Dict[str, Any]:
        """Génère un comportement de remplissage de formulaire."""
        behaviors = {
            'careful': {
                'field_delay': (2, 5),
                'review_probability': 0.8,
                'correction_probability': 0.3
            },
            'normal': {
                'field_delay': (1, 3),
                'review_probability': 0.5,
                'correction_probability': 0.1
            },
            'rushed': {
                'field_delay': (0.5, 1.5),
                'review_probability': 0.2,
                'correction_probability': 0.05
            }
        }
        
        return behaviors.get(pattern, behaviors['normal'])
    
    def generate_realistic_pause(self, context: str = 'general') -> float:
        """Génère une pause réaliste basée sur le contexte."""
        pause_durations = {
            'reading': (2, 8),
            'thinking': (1, 3),
            'typing': (0.5, 2),
            'navigation': (0.5, 1.5),
            'general': (0.5, 3)
        }
        
        min_pause, max_pause = pause_durations.get(context, pause_durations['general'])
        return random.uniform(min_pause, max_pause)
    
    def get_device_characteristics(self, device_type: str = 'desktop') -> Dict[str, Any]:
        """Génère des caractéristiques réalistes pour différents appareils."""
        characteristics = {
            'desktop': {
                'screen_size': (1920, 1080),
                'scroll_speed': (100, 300),
                'click_accuracy': 0.95,
                'typing_speed': 'normal'
            },
            'laptop': {
                'screen_size': (1366, 768),
                'scroll_speed': (80, 250),
                'click_accuracy': 0.90,
                'typing_speed': 'normal'
            },
            'tablet': {
                'screen_size': (768, 1024),
                'scroll_speed': (50, 150),
                'click_accuracy': 0.85,
                'typing_speed': 'slow'
            },
            'mobile': {
                'screen_size': (375, 667),
                'scroll_speed': (30, 100),
                'click_accuracy': 0.80,
                'typing_speed': 'slow'
            }
        }
        
        return characteristics.get(device_type, characteristics['desktop'])
