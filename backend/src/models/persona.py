"""
Persona model for traffic simulation platform.
Represents user behavior profiles for simulation.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Persona(Base):
    """Persona model representing user behavior profiles."""
    
    __tablename__ = 'personas'
    
    # Primary key
    id: UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Basic information
    name: str = Column(String(100), nullable=False, unique=True)
    description: Optional[str] = Column(Text, nullable=True)
    
    # Session duration configuration
    session_duration_min: int = Column(Integer, nullable=False)
    session_duration_max: int = Column(Integer, nullable=False)
    
    # Page navigation configuration
    pages_min: int = Column(Integer, nullable=False)
    pages_max: int = Column(Integer, nullable=False)
    
    # Action configuration
    actions_per_page_min: int = Column(Integer, nullable=False, server_default='1')
    actions_per_page_max: int = Column(Integer, nullable=False, server_default='10')
    
    # Behavioral probabilities (0.0 to 1.0)
    scroll_probability: Decimal = Column(Numeric(3, 2), nullable=False, server_default='0.8')
    click_probability: Decimal = Column(Numeric(3, 2), nullable=False, server_default='0.6')
    typing_probability: Decimal = Column(Numeric(3, 2), nullable=False, server_default='0.1')
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="persona")
    sessions = relationship("Session", back_populates="persona")
    session_analytics = relationship("SessionAnalytics", back_populates="persona")
    
    # Check constraints
    __table_args__ = (
        CheckConstraint('session_duration_min > 0', name='ck_personas_session_duration_min_positive'),
        CheckConstraint('session_duration_max >= session_duration_min', name='ck_personas_session_duration_max_gte_min'),
        CheckConstraint('pages_min > 0', name='ck_personas_pages_min_positive'),
        CheckConstraint('pages_max >= pages_min', name='ck_personas_pages_max_gte_min'),
        CheckConstraint('scroll_probability BETWEEN 0 AND 1', name='ck_personas_scroll_probability_range'),
        CheckConstraint('click_probability BETWEEN 0 AND 1', name='ck_personas_click_probability_range'),
        CheckConstraint('typing_probability BETWEEN 0 AND 1', name='ck_personas_typing_probability_range'),
    )
    
    def __repr__(self) -> str:
        return f"<Persona(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convert persona to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'session_duration_min': self.session_duration_min,
            'session_duration_max': self.session_duration_max,
            'pages_min': self.pages_min,
            'pages_max': self.pages_max,
            'actions_per_page_min': self.actions_per_page_min,
            'actions_per_page_max': self.actions_per_page_max,
            'scroll_probability': float(self.scroll_probability),
            'click_probability': float(self.click_probability),
            'typing_probability': float(self.typing_probability),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Persona':
        """Create persona from dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description'),
            session_duration_min=data['session_duration_min'],
            session_duration_max=data['session_duration_max'],
            pages_min=data['pages_min'],
            pages_max=data['pages_max'],
            actions_per_page_min=data.get('actions_per_page_min', 1),
            actions_per_page_max=data.get('actions_per_page_max', 10),
            scroll_probability=Decimal(str(data.get('scroll_probability', 0.8))),
            click_probability=Decimal(str(data.get('click_probability', 0.6))),
            typing_probability=Decimal(str(data.get('typing_probability', 0.1)))
        )
