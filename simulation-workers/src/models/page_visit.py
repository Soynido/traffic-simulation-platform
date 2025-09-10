"""
Modèle PageVisit pour les simulation workers.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class PageVisit:
    """Modèle PageVisit pour les simulation workers."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.session_id = kwargs.get('session_id')
        self.url = kwargs.get('url')
        self.page_number = kwargs.get('page_number', 1)
        self.load_time = kwargs.get('load_time', 0.0)
        self.title = kwargs.get('title')
        self.viewport_width = kwargs.get('viewport_width', 1920)
        self.viewport_height = kwargs.get('viewport_height', 1080)
        self.created_at = kwargs.get('created_at')
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'url': self.url,
            'page_number': self.page_number,
            'load_time': self.load_time,
            'title': self.title,
            'viewport_width': self.viewport_width,
            'viewport_height': self.viewport_height,
            'created_at': self.created_at
        }
