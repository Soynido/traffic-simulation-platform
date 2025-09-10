"""
Modèle Session pour les simulation workers.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid


class Session:
    """Modèle Session pour les simulation workers."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.campaign_id = kwargs.get('campaign_id')
        self.persona_id = kwargs.get('persona_id')
        self.start_url = kwargs.get('start_url')
        self.user_agent = kwargs.get('user_agent')
        self.viewport_width = kwargs.get('viewport_width', 1920)
        self.viewport_height = kwargs.get('viewport_height', 1080)
        self.status = kwargs.get('status', 'pending')
        self.pages_visited = kwargs.get('pages_visited', 0)
        self.actions_performed = kwargs.get('actions_performed', 0)
        self.total_duration = kwargs.get('total_duration', 0.0)
        self.rhythm_score = kwargs.get('rhythm_score', 0.0)
        self.detection_risk = kwargs.get('detection_risk', 0.0)
        self.error_message = kwargs.get('error_message')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        self.started_at = kwargs.get('started_at')
        self.completed_at = kwargs.get('completed_at')
    
    def to_dict(self):
        """Convertit le modèle en dictionnaire."""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'persona_id': self.persona_id,
            'start_url': self.start_url,
            'user_agent': self.user_agent,
            'viewport_width': self.viewport_width,
            'viewport_height': self.viewport_height,
            'status': self.status,
            'pages_visited': self.pages_visited,
            'actions_performed': self.actions_performed,
            'total_duration': self.total_duration,
            'rhythm_score': self.rhythm_score,
            'detection_risk': self.detection_risk,
            'error_message': self.error_message,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }
