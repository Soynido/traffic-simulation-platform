"""
Modèle Persona pour les simulation workers.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class Persona:
    """Modèle Persona pour les simulation workers."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.session_duration_min = kwargs.get('session_duration_min', 60)
        self.session_duration_max = kwargs.get('session_duration_max', 300)
        self.pages_min = kwargs.get('pages_min', 1)
        self.pages_max = kwargs.get('pages_max', 5)
        self.actions_per_page_min = kwargs.get('actions_per_page_min', 1)
        self.actions_per_page_max = kwargs.get('actions_per_page_max', 10)
        self.scroll_probability = kwargs.get('scroll_probability', 0.8)
        self.click_probability = kwargs.get('click_probability', 0.6)
        self.typing_probability = kwargs.get('typing_probability', 0.1)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'session_duration_min': self.session_duration_min,
            'session_duration_max': self.session_duration_max,
            'pages_min': self.pages_min,
            'pages_max': self.pages_max,
            'actions_per_page_min': self.actions_per_page_min,
            'actions_per_page_max': self.actions_per_page_max,
            'scroll_probability': self.scroll_probability,
            'click_probability': self.click_probability,
            'typing_probability': self.typing_probability,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
