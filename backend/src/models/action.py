"""
Action model for traffic simulation platform.
Represents user actions within page visits.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class ActionType(str, Enum):
    """Action type enumeration."""
    CLICK = 'click'
    DOUBLE_CLICK = 'double_click'
    RIGHT_CLICK = 'right_click'
    SCROLL = 'scroll'
    SCROLL_TO_ELEMENT = 'scroll_to_element'
    TYPE = 'type'
    CLEAR = 'clear'
    SELECT = 'select'
    HOVER = 'hover'
    DRAG_AND_DROP = 'drag_and_drop'
    KEY_PRESS = 'key_press'
    PAGE_LOAD = 'page_load'
    PAGE_UNLOAD = 'page_unload'


class Action(Base):
    """Action model representing user actions within page visits."""
    
    __tablename__ = 'actions'
    
    # Primary key
    id: UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Foreign key
    page_visit_id: UUID = Column(PostgresUUID(as_uuid=True), ForeignKey('page_visits.id', ondelete='CASCADE'), nullable=False)
    
    # Action details
    action_type: ActionType = Column(ENUM(ActionType, name='action_type'), nullable=False)
    action_order: int = Column(Integer, nullable=False)
    timestamp: datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    duration_ms: int = Column(Integer, nullable=False, server_default='0')
    
    # Element information
    element_selector: Optional[str] = Column(Text, nullable=True)
    element_text: Optional[str] = Column(Text, nullable=True)
    coordinates_x: Optional[int] = Column(Integer, nullable=True)
    coordinates_y: Optional[int] = Column(Integer, nullable=True)
    input_value: Optional[str] = Column(Text, nullable=True)
    
    # Relationships
    page_visit = relationship("PageVisit", back_populates="actions")
    
    # Check constraints
    __table_args__ = (
        CheckConstraint('action_order > 0', name='ck_actions_action_order_positive'),
    )
    
    def __repr__(self) -> str:
        return f"<Action(id={self.id}, page_visit_id={self.page_visit_id}, type='{self.action_type}', order={self.action_order})>"
    
    def to_dict(self) -> dict:
        """Convert action to dictionary."""
        return {
            'id': str(self.id),
            'page_visit_id': str(self.page_visit_id),
            'action_type': self.action_type.value,
            'action_order': self.action_order,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration_ms': self.duration_ms,
            'element_selector': self.element_selector,
            'element_text': self.element_text,
            'coordinates_x': self.coordinates_x,
            'coordinates_y': self.coordinates_y,
            'input_value': self.input_value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Action':
        """Create action from dictionary."""
        return cls(
            page_visit_id=UUID(data['page_visit_id']),
            action_type=ActionType(data['action_type']),
            action_order=data['action_order'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')) if data.get('timestamp') else datetime.utcnow(),
            duration_ms=data.get('duration_ms', 0),
            element_selector=data.get('element_selector'),
            element_text=data.get('element_text'),
            coordinates_x=data.get('coordinates_x'),
            coordinates_y=data.get('coordinates_y'),
            input_value=data.get('input_value')
        )
    
    @classmethod
    def create_click(cls, page_visit_id: UUID, element_selector: str, x: int, y: int, order: int) -> 'Action':
        """Create a click action."""
        return cls(
            page_visit_id=page_visit_id,
            action_type=ActionType.CLICK,
            action_order=order,
            element_selector=element_selector,
            coordinates_x=x,
            coordinates_y=y
        )
    
    @classmethod
    def create_scroll(cls, page_visit_id: UUID, x: int, y: int, order: int) -> 'Action':
        """Create a scroll action."""
        return cls(
            page_visit_id=page_visit_id,
            action_type=ActionType.SCROLL,
            action_order=order,
            coordinates_x=x,
            coordinates_y=y
        )
    
    @classmethod
    def create_type(cls, page_visit_id: UUID, element_selector: str, text: str, order: int) -> 'Action':
        """Create a type action."""
        return cls(
            page_visit_id=page_visit_id,
            action_type=ActionType.TYPE,
            action_order=order,
            element_selector=element_selector,
            input_value=text
        )
    
    @classmethod
    def create_hover(cls, page_visit_id: UUID, element_selector: str, x: int, y: int, order: int) -> 'Action':
        """Create a hover action."""
        return cls(
            page_visit_id=page_visit_id,
            action_type=ActionType.HOVER,
            action_order=order,
            element_selector=element_selector,
            coordinates_x=x,
            coordinates_y=y
        )
