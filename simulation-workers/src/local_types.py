"""
Types locaux pour les simulation workers
Simplifiés pour éviter les dépendances complexes
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


class Persona:
    """Persona simplifié pour les workers"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.behaviorProfile = kwargs.get('behaviorProfile', {})
        self.demographics = kwargs.get('demographics', {})
        self.technicalProfile = kwargs.get('technicalProfile', {})
        self.isActive = kwargs.get('isActive', True)
        self.createdAt = kwargs.get('createdAt', datetime.now())
        self.updatedAt = kwargs.get('updatedAt', datetime.now())


class Campaign:
    """Campagne simplifiée pour les workers"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.targetUrl = kwargs.get('targetUrl')
        self.personaIds = kwargs.get('personaIds', [])
        self.simulationConfig = kwargs.get('simulationConfig', {})
        self.status = kwargs.get('status', 'draft')
        self.metrics = kwargs.get('metrics', {})
        self.createdAt = kwargs.get('createdAt', datetime.now())
        self.updatedAt = kwargs.get('updatedAt', datetime.now())


class Session:
    """Session simplifiée pour les workers"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.campaignId = kwargs.get('campaignId')
        self.personaId = kwargs.get('personaId')
        self.status = kwargs.get('status', 'pending')
        self.startedAt = kwargs.get('startedAt')
        self.completedAt = kwargs.get('completedAt')
        self.metrics = kwargs.get('metrics', {})


class PageVisit:
    """Page visit simplifiée pour les workers"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.sessionId = kwargs.get('sessionId')
        self.url = kwargs.get('url')
        self.timestamp = kwargs.get('timestamp', datetime.now())
        self.duration = kwargs.get('duration', 0)


class Action:
    """Action simplifiée pour les workers"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.sessionId = kwargs.get('sessionId')
        self.type = kwargs.get('type')
        self.timestamp = kwargs.get('timestamp', datetime.now())
        self.data = kwargs.get('data', {})
