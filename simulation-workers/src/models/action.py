"""
Modèle Action pour les simulation workers.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class Action:
    """Modèle Action pour les simulation workers."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.session_id = kwargs.get('session_id')
        self.page_number = kwargs.get('page_number', 1)
        self.action_type = kwargs.get('action_type')
        self.timestamp = kwargs.get('timestamp', 0.0)
        self.details = kwargs.get('details', {})
        self.created_at = kwargs.get('created_at')
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'page_number': self.page_number,
            'action_type': self.action_type,
            'timestamp': self.timestamp,
            'details': self.details,
            'created_at': self.created_at
        }
