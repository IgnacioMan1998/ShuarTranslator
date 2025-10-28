"""Base repository interface with common functionality."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any
from uuid import UUID

# Generic type for entities
T = TypeVar('T')


class IBaseRepository(Generic[T], ABC):
    """Base repository interface with common CRUD operations."""
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save an entity to the repository."""
        pass
    
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """Find an entity by its unique identifier."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its ID."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """Check if an entity exists by its ID."""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Get total count of entities."""
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Find all entities with pagination."""
        pass
    
    @abstractmethod
    async def bulk_save(self, entities: List[T]) -> List[T]:
        """Save multiple entities in a single operation."""
        pass


class ISearchableRepository(Generic[T], ABC):
    """Interface for repositories that support search functionality."""
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[T]:
        """Search entities with optional filters."""
        pass
    
    @abstractmethod
    async def search_count(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Get count of search results."""
        pass


class IAnalyticsRepository(ABC):
    """Interface for repositories that provide analytics functionality."""
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        pass
    
    @abstractmethod
    async def get_trends(
        self, 
        metric: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get trends for a specific metric."""
        pass
    
    @abstractmethod
    async def get_top_items(
        self, 
        metric: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top items by a specific metric."""
        pass


class IUnitOfWork(ABC):
    """Unit of Work interface for managing transactions across repositories."""
    
    @abstractmethod
    async def begin_transaction(self) -> None:
        """Begin a database transaction."""
        pass
    
    @abstractmethod
    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass
    
    @abstractmethod
    async def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        pass
    
    @abstractmethod
    async def save_changes(self) -> None:
        """Save all pending changes."""
        pass
    
    @property
    @abstractmethod
    def word_repository(self) -> 'IWordRepository':
        """Get word repository instance."""
        pass
    
    @property
    @abstractmethod
    def translation_repository(self) -> 'ITranslationRepository':
        """Get translation repository instance."""
        pass
    
    @property
    @abstractmethod
    def feedback_repository(self) -> 'IFeedbackRepository':
        """Get feedback repository instance."""
        pass
    
    @property
    @abstractmethod
    def phonological_repository(self) -> 'IPhonologicalRepository':
        """Get phonological repository instance."""
        pass
    
    @property
    @abstractmethod
    def user_repository(self) -> 'IUserRepository':
        """Get user repository instance."""
        pass


# Import the specific repository interfaces for type hints
from app.features.translation.domain.repositories.word_repository import IWordRepository
from app.features.translation.domain.repositories.translation_repository import ITranslationRepository
from app.features.feedback.domain.repositories.feedback_repository import IFeedbackRepository
from app.features.translation.domain.repositories.phonological_repository import IPhonologicalRepository
from app.features.admin.domain.repositories.user_repository import IUserRepository