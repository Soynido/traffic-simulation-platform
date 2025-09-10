"""
Calculateur de rythme pour la simulation de trafic.
Analyse les patterns de comportement pour détecter l'humanité des interactions.
"""
import math
import statistics
from typing import List, Dict, Any, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class RhythmEvent:
    """Événement de rythme pour l'analyse."""
    timestamp: float
    event_type: str
    details: Dict[str, Any]


class RhythmCalculator:
    """Calculateur de rythme et de détection de bots."""
    
    def __init__(self):
        # Seuils pour l'analyse de rythme
        self.thresholds = {
            'typing_speed_min': 50,      # ms entre les frappes
            'typing_speed_max': 500,     # ms entre les frappes
            'scroll_speed_min': 100,     # ms entre les scrolls
            'scroll_speed_max': 2000,    # ms entre les scrolls
            'click_delay_min': 50,       # ms entre les clics
            'click_delay_max': 1000,     # ms entre les clics
            'action_interval_min': 200,  # ms entre les actions
            'action_interval_max': 5000, # ms entre les actions
        }
        
        # Patterns humains typiques
        self.human_patterns = {
            'typing_rhythm': {
                'variance_threshold': 0.3,  # Variance acceptable
                'pause_probability': 0.1,   # Probabilité de pause
                'error_rate': 0.02,         # Taux d'erreur typique
            },
            'scroll_rhythm': {
                'variance_threshold': 0.4,
                'pause_probability': 0.2,
                'backtrack_probability': 0.1,
            },
            'click_rhythm': {
                'variance_threshold': 0.3,
                'double_click_probability': 0.05,
                'hover_time_variance': 0.5,
            }
        }
    
    def calculate_rhythm_score(self, events: List[Dict[str, Any]]) -> float:
        """Calcule un score de rythme global (0-1, 1 = très humain)."""
        if not events:
            return 0.0
        
        # Convertir les événements en objets RhythmEvent
        rhythm_events = self._convert_to_rhythm_events(events)
        
        # Calculer les scores individuels
        typing_score = self._calculate_typing_rhythm_score(rhythm_events)
        scroll_score = self._calculate_scroll_rhythm_score(rhythm_events)
        click_score = self._calculate_click_rhythm_score(rhythm_events)
        timing_score = self._calculate_timing_rhythm_score(rhythm_events)
        
        # Score global pondéré
        weights = {
            'typing': 0.3,
            'scroll': 0.3,
            'click': 0.2,
            'timing': 0.2
        }
        
        global_score = (
            typing_score * weights['typing'] +
            scroll_score * weights['scroll'] +
            click_score * weights['click'] +
            timing_score * weights['timing']
        )
        
        return min(1.0, max(0.0, global_score))
    
    def calculate_detection_risk(self, events: List[Dict[str, Any]]) -> float:
        """Calcule le risque de détection (0-1, 1 = très risqué)."""
        if not events:
            return 1.0
        
        rhythm_events = self._convert_to_rhythm_events(events)
        
        # Facteurs de risque
        risk_factors = {
            'too_fast': self._detect_too_fast_actions(rhythm_events),
            'too_regular': self._detect_too_regular_patterns(rhythm_events),
            'no_pauses': self._detect_no_pauses(rhythm_events),
            'perfect_accuracy': self._detect_perfect_accuracy(rhythm_events),
            'unrealistic_timing': self._detect_unrealistic_timing(rhythm_events),
        }
        
        # Calculer le risque global
        total_risk = sum(risk_factors.values()) / len(risk_factors)
        
        return min(1.0, max(0.0, total_risk))
    
    def _convert_to_rhythm_events(self, events: List[Dict[str, Any]]) -> List[RhythmEvent]:
        """Convertit les événements en objets RhythmEvent."""
        rhythm_events = []
        
        for event in events:
            rhythm_event = RhythmEvent(
                timestamp=event.get('timestamp', 0),
                event_type=event.get('type', 'unknown'),
                details=event.get('details', {})
            )
            rhythm_events.append(rhythm_event)
        
        # Trier par timestamp
        rhythm_events.sort(key=lambda x: x.timestamp)
        
        return rhythm_events
    
    def _calculate_typing_rhythm_score(self, events: List[RhythmEvent]) -> float:
        """Calcule le score de rythme de frappe."""
        typing_events = [e for e in events if e.event_type == 'typing']
        
        if len(typing_events) < 2:
            return 0.5  # Score neutre si pas assez d'événements
        
        # Calculer les intervalles entre les frappes
        intervals = []
        for i in range(1, len(typing_events)):
            interval = typing_events[i].timestamp - typing_events[i-1].timestamp
            intervals.append(interval * 1000)  # Convertir en ms
        
        if not intervals:
            return 0.5
        
        # Vérifier la variance
        mean_interval = statistics.mean(intervals)
        variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        coefficient_of_variation = math.sqrt(variance) / mean_interval if mean_interval > 0 else 0
        
        # Score basé sur la variance (plus de variance = plus humain)
        variance_score = min(1.0, coefficient_of_variation / self.human_patterns['typing_rhythm']['variance_threshold'])
        
        # Vérifier les pauses
        pause_score = self._calculate_pause_score(intervals)
        
        # Score global
        return (variance_score + pause_score) / 2
    
    def _calculate_scroll_rhythm_score(self, events: List[RhythmEvent]) -> float:
        """Calcule le score de rythme de scroll."""
        scroll_events = [e for e in events if e.event_type == 'scroll']
        
        if len(scroll_events) < 2:
            return 0.5
        
        # Calculer les intervalles entre les scrolls
        intervals = []
        for i in range(1, len(scroll_events)):
            interval = scroll_events[i].timestamp - scroll_events[i-1].timestamp
            intervals.append(interval * 1000)
        
        if not intervals:
            return 0.5
        
        # Vérifier la variance
        mean_interval = statistics.mean(intervals)
        variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        coefficient_of_variation = math.sqrt(variance) / mean_interval if mean_interval > 0 else 0
        
        variance_score = min(1.0, coefficient_of_variation / self.human_patterns['scroll_rhythm']['variance_threshold'])
        
        # Vérifier les pauses
        pause_score = self._calculate_pause_score(intervals)
        
        # Vérifier les retours en arrière
        backtrack_score = self._calculate_backtrack_score(scroll_events)
        
        return (variance_score + pause_score + backtrack_score) / 3
    
    def _calculate_click_rhythm_score(self, events: List[RhythmEvent]) -> float:
        """Calcule le score de rythme de clic."""
        click_events = [e for e in events if e.event_type == 'click']
        
        if len(click_events) < 2:
            return 0.5
        
        # Calculer les intervalles entre les clics
        intervals = []
        for i in range(1, len(click_events)):
            interval = click_events[i].timestamp - click_events[i-1].timestamp
            intervals.append(interval * 1000)
        
        if not intervals:
            return 0.5
        
        # Vérifier la variance
        mean_interval = statistics.mean(intervals)
        variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        coefficient_of_variation = math.sqrt(variance) / mean_interval if mean_interval > 0 else 0
        
        variance_score = min(1.0, coefficient_of_variation / self.human_patterns['click_rhythm']['variance_threshold'])
        
        # Vérifier les pauses
        pause_score = self._calculate_pause_score(intervals)
        
        # Vérifier les double-clics
        double_click_score = self._calculate_double_click_score(click_events)
        
        return (variance_score + pause_score + double_click_score) / 3
    
    def _calculate_timing_rhythm_score(self, events: List[RhythmEvent]) -> float:
        """Calcule le score de rythme temporel global."""
        if len(events) < 2:
            return 0.5
        
        # Calculer les intervalles entre tous les événements
        intervals = []
        for i in range(1, len(events)):
            interval = events[i].timestamp - events[i-1].timestamp
            intervals.append(interval * 1000)
        
        if not intervals:
            return 0.5
        
        # Vérifier la distribution des intervalles
        mean_interval = statistics.mean(intervals)
        variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        coefficient_of_variation = math.sqrt(variance) / mean_interval if mean_interval > 0 else 0
        
        # Score basé sur la variance
        variance_score = min(1.0, coefficient_of_variation / 0.5)
        
        # Vérifier les pauses
        pause_score = self._calculate_pause_score(intervals)
        
        return (variance_score + pause_score) / 2
    
    def _calculate_pause_score(self, intervals: List[float]) -> float:
        """Calcule le score basé sur les pauses."""
        if not intervals:
            return 0.0
        
        # Identifier les pauses (intervalles > 1 seconde)
        pauses = [interval for interval in intervals if interval > 1000]
        pause_ratio = len(pauses) / len(intervals)
        
        # Score basé sur la présence de pauses
        return min(1.0, pause_ratio / 0.2)  # 20% de pauses est normal
    
    def _calculate_backtrack_score(self, scroll_events: List[RhythmEvent]) -> float:
        """Calcule le score basé sur les retours en arrière."""
        if len(scroll_events) < 3:
            return 0.5
        
        # Analyser les positions de scroll
        positions = []
        for event in scroll_events:
            position = event.details.get('position', 0)
            positions.append(position)
        
        # Compter les retours en arrière
        backtracks = 0
        for i in range(1, len(positions)):
            if positions[i] < positions[i-1]:
                backtracks += 1
        
        backtrack_ratio = backtracks / (len(positions) - 1)
        
        # Score basé sur les retours en arrière
        return min(1.0, backtrack_ratio / 0.1)  # 10% de retours est normal
    
    def _calculate_double_click_score(self, click_events: List[RhythmEvent]) -> float:
        """Calcule le score basé sur les double-clics."""
        if len(click_events) < 2:
            return 0.5
        
        # Identifier les double-clics (clics < 500ms d'intervalle)
        double_clicks = 0
        for i in range(1, len(click_events)):
            interval = (click_events[i].timestamp - click_events[i-1].timestamp) * 1000
            if interval < 500:
                double_clicks += 1
        
        double_click_ratio = double_clicks / (len(click_events) - 1)
        
        # Score basé sur les double-clics
        return min(1.0, double_click_ratio / 0.05)  # 5% de double-clics est normal
    
    def _detect_too_fast_actions(self, events: List[RhythmEvent]) -> float:
        """Détecte les actions trop rapides."""
        if len(events) < 2:
            return 0.0
        
        # Calculer les intervalles
        intervals = []
        for i in range(1, len(events)):
            interval = (events[i].timestamp - events[i-1].timestamp) * 1000
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Compter les actions trop rapides
        too_fast = sum(1 for interval in intervals if interval < 50)
        too_fast_ratio = too_fast / len(intervals)
        
        return min(1.0, too_fast_ratio / 0.1)  # 10% d'actions trop rapides est suspect
    
    def _detect_too_regular_patterns(self, events: List[RhythmEvent]) -> float:
        """Détecte les patterns trop réguliers."""
        if len(events) < 3:
            return 0.0
        
        # Calculer les intervalles
        intervals = []
        for i in range(1, len(events)):
            interval = (events[i].timestamp - events[i-1].timestamp) * 1000
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Calculer la variance
        variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        mean_interval = statistics.mean(intervals)
        coefficient_of_variation = math.sqrt(variance) / mean_interval if mean_interval > 0 else 0
        
        # Score basé sur la régularité (moins de variance = plus suspect)
        return max(0.0, 1.0 - coefficient_of_variation / 0.1)  # CV < 0.1 est suspect
    
    def _detect_no_pauses(self, events: List[RhythmEvent]) -> float:
        """Détecte l'absence de pauses."""
        if len(events) < 2:
            return 0.0
        
        # Calculer les intervalles
        intervals = []
        for i in range(1, len(events)):
            interval = (events[i].timestamp - events[i-1].timestamp) * 1000
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Compter les pauses
        pauses = sum(1 for interval in intervals if interval > 1000)
        pause_ratio = pauses / len(intervals)
        
        # Score basé sur l'absence de pauses
        return max(0.0, 1.0 - pause_ratio / 0.2)  # < 20% de pauses est suspect
    
    def _detect_perfect_accuracy(self, events: List[RhythmEvent]) -> float:
        """Détecte une précision parfaite (suspecte)."""
        # Analyser les événements de frappe
        typing_events = [e for e in events if e.event_type == 'typing']
        
        if len(typing_events) < 5:
            return 0.0
        
        # Vérifier s'il y a des erreurs de frappe
        errors = 0
        for event in typing_events:
            if 'error' in event.details:
                errors += 1
        
        error_ratio = errors / len(typing_events)
        
        # Score basé sur l'absence d'erreurs
        return max(0.0, 1.0 - error_ratio / 0.02)  # < 2% d'erreurs est suspect
    
    def _detect_unrealistic_timing(self, events: List[RhythmEvent]) -> float:
        """Détecte des timings irréalistes."""
        if len(events) < 2:
            return 0.0
        
        # Calculer les intervalles
        intervals = []
        for i in range(1, len(events)):
            interval = (events[i].timestamp - events[i-1].timestamp) * 1000
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Vérifier les intervalles irréalistes
        unrealistic = 0
        for interval in intervals:
            if interval < 10 or interval > 30000:  # < 10ms ou > 30s
                unrealistic += 1
        
        unrealistic_ratio = unrealistic / len(intervals)
        
        return min(1.0, unrealistic_ratio / 0.05)  # 5% d'intervalles irréalistes est suspect
    
    def get_rhythm_analysis(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Obtient une analyse complète du rythme."""
        rhythm_events = self._convert_to_rhythm_events(events)
        
        return {
            'rhythm_score': self.calculate_rhythm_score(events),
            'detection_risk': self.calculate_detection_risk(events),
            'typing_score': self._calculate_typing_rhythm_score(rhythm_events),
            'scroll_score': self._calculate_scroll_rhythm_score(rhythm_events),
            'click_score': self._calculate_click_rhythm_score(rhythm_events),
            'timing_score': self._calculate_timing_rhythm_score(rhythm_events),
            'total_events': len(events),
            'event_types': list(set(e.get('type', 'unknown') for e in events)),
            'analysis_timestamp': events[-1].get('timestamp', 0) if events else 0
        }
