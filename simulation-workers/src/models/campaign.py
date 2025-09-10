"""
Modèle Campaign pour les simulation workers.
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class Campaign:
    """Modèle Campaign pour les simulation workers."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.target_url = kwargs.get('target_url')
        self.total_sessions = kwargs.get('total_sessions', 100)
        self.concurrent_sessions = kwargs.get('concurrent_sessions', 10)
        self.status = kwargs.get('status', 'pending')
        self.persona_id = kwargs.get('persona_id')
        self.rate_limit_delay_ms = kwargs.get('rate_limit_delay_ms', 1000)
        self.user_agent_rotation = kwargs.get('user_agent_rotation', True)
        self.respect_robots_txt = kwargs.get('respect_robots_txt', True)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.started_at = kwargs.get('started_at')
        self.completed_at = kwargs.get('completed_at')
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_url': self.target_url,
            'total_sessions': self.total_sessions,
            'concurrent_sessions': self.concurrent_sessions,
            'status': self.status,
            'persona_id': self.persona_id,
            'rate_limit_delay_ms': self.rate_limit_delay_ms,
            'user_agent_rotation': self.user_agent_rotation,
            'respect_robots_txt': self.respect_robots_txt,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }
