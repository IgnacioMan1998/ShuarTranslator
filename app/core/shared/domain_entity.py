"""Base domain entity class with common functionality."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class DomainEntity(ABC):
    """Base class for all domain entities."""
    
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization hook for validation."""
        self.validate()
    
    @abstractmethod
    def validate(self) -> None:
        """Validate entity invariants. Must be implemented by subclasses."""
        pass
    
    def mark_as_updated(self) -> None:
        """Mark entity as updated with current timestamp."""
        self.updated_at = datetime.now()
    
    def is_same_entity(self, other: 'DomainEntity') -> bool:
        """Check if this entity is the same as another based on ID."""
        return isinstance(other, self.__class__) and self.id == other.id
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation. Must be implemented by subclasses."""
        pass


@dataclass
class AggregateRoot(DomainEntity):
    """Base class for aggregate roots in DDD."""
    
    _domain_events: List[Any] = field(default_factory=list, init=False)
    
    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to be published."""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
    
    def get_domain_events(self) -> List[Any]:
        """Get all domain events."""
        return self._domain_events.copy()
    
    def has_domain_events(self) -> bool:
        """Check if there are any domain events."""
        return len(self._domain_events) > 0