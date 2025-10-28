"""Translation repository interface for domain layer."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.features.translation.domain.entities.translation import Translation, Language, TranslationStatus


class ITranslationRepository(ABC):
    """Interface for Translation repository following repository pattern."""
    
    @abstractmethod
    async def save(self, translation: Translation) -> Translation:
        """Save a translation entity to the repository."""
        pass
    
    @abstractmethod
    async def find_by_id(self, translation_id: UUID) -> Optional[Translation]:
        """Find a translation by its unique identifier."""
        pass
    
    @abstractmethod
    async def find_by_source_text(
        self, 
        source_text: str, 
        source_language: Language
    ) -> List[Translation]:
        """Find translations by source text and language."""
        pass
    
    @abstractmethod
    async def find_by_target_text(
        self, 
        target_text: str, 
        target_language: Language
    ) -> List[Translation]:
        """Find translations by target text and language."""
        pass
    
    @abstractmethod
    async def find_bidirectional_pair(
        self, 
        text1: str, 
        text2: str
    ) -> Optional[List[Translation]]:
        """Find bidirectional translation pairs (A->B and B->A)."""
        pass
    
    @abstractmethod
    async def find_by_language_pair(
        self, 
        source_language: Language, 
        target_language: Language,
        limit: int = 100
    ) -> List[Translation]:
        """Find translations for a specific language pair."""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: TranslationStatus) -> List[Translation]:
        """Find translations by their approval status."""
        pass
    
    @abstractmethod
    async def find_pending_approval(self) -> List[Translation]:
        """Find translations pending expert approval."""
        pass
    
    @abstractmethod
    async def find_needs_review(self) -> List[Translation]:
        """Find translations that need expert review."""
        pass
    
    @abstractmethod
    async def find_by_creator(self, creator_id: UUID) -> List[Translation]:
        """Find translations created by a specific user."""
        pass
    
    @abstractmethod
    async def find_by_approver(self, approver_id: UUID) -> List[Translation]:
        """Find translations approved by a specific expert."""
        pass
    
    @abstractmethod
    async def find_high_rated(
        self, 
        min_rating: float = 4.0, 
        min_total_ratings: int = 3
    ) -> List[Translation]:
        """Find highly rated translations."""
        pass
    
    @abstractmethod
    async def find_low_rated(
        self, 
        max_rating: float = 2.0, 
        min_total_ratings: int = 3
    ) -> List[Translation]:
        """Find poorly rated translations that may need review."""
        pass
    
    @abstractmethod
    async def find_most_used(self, limit: int = 100) -> List[Translation]:
        """Find most frequently used translations."""
        pass
    
    @abstractmethod
    async def find_recently_created(
        self, 
        since: datetime, 
        limit: int = 50
    ) -> List[Translation]:
        """Find translations created since a specific date."""
        pass
    
    @abstractmethod
    async def find_recently_updated(
        self, 
        since: datetime, 
        limit: int = 50
    ) -> List[Translation]:
        """Find translations updated since a specific date."""
        pass
    
    @abstractmethod
    async def find_by_confidence_range(
        self, 
        min_confidence: float, 
        max_confidence: float
    ) -> List[Translation]:
        """Find translations within a confidence score range."""
        pass
    
    @abstractmethod
    async def find_with_word_references(self, word_ids: List[UUID]) -> List[Translation]:
        """Find translations that reference specific words."""
        pass
    
    @abstractmethod
    async def search_translations(
        self, 
        query: str, 
        language: Optional[Language] = None,
        limit: int = 50
    ) -> List[Translation]:
        """Perform full-text search across translation texts."""
        pass
    
    @abstractmethod
    async def get_translation_statistics(self) -> Dict[str, Any]:
        """Get repository statistics for translations."""
        pass
    
    @abstractmethod
    async def get_usage_analytics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get usage analytics for a date range."""
        pass
    
    @abstractmethod
    async def update(self, translation: Translation) -> Translation:
        """Update an existing translation entity."""
        pass
    
    @abstractmethod
    async def delete(self, translation_id: UUID) -> bool:
        """Delete a translation by its ID."""
        pass
    
    @abstractmethod
    async def exists(self, translation_id: UUID) -> bool:
        """Check if a translation exists by its ID."""
        pass
    
    @abstractmethod
    async def exists_exact_match(
        self, 
        source_text: str, 
        target_text: str, 
        source_language: Language, 
        target_language: Language
    ) -> bool:
        """Check if an exact translation match already exists."""
        pass
    
    @abstractmethod
    async def bulk_save(self, translations: List[Translation]) -> List[Translation]:
        """Save multiple translations in a single operation."""
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        translation_ids: List[UUID], 
        status: TranslationStatus,
        updated_by: UUID
    ) -> int:
        """Bulk update status for multiple translations."""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Get total count of translations."""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: TranslationStatus) -> int:
        """Get count of translations by status."""
        pass
    
    @abstractmethod
    async def count_by_language_pair(
        self, 
        source_language: Language, 
        target_language: Language
    ) -> int:
        """Get count of translations for a language pair."""
        pass
    
    @abstractmethod
    async def get_average_rating(self) -> float:
        """Get average rating across all translations."""
        pass
    
    @abstractmethod
    async def get_average_confidence(self) -> float:
        """Get average confidence score across all translations."""
        pass