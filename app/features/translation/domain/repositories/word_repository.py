"""Word repository interface for domain layer."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.features.translation.domain.entities.word import Word, WordType, VocalType


class IWordRepository(ABC):
    """Interface for Word repository following repository pattern."""
    
    @abstractmethod
    async def save(self, word: Word) -> Word:
        """Save a word entity to the repository."""
        pass
    
    @abstractmethod
    async def find_by_id(self, word_id: UUID) -> Optional[Word]:
        """Find a word by its unique identifier."""
        pass
    
    @abstractmethod
    async def find_by_shuar_text(self, shuar_text: str) -> Optional[Word]:
        """Find a word by its Shuar text (exact match)."""
        pass
    
    @abstractmethod
    async def find_by_spanish_translation(self, spanish_text: str) -> List[Word]:
        """Find words by Spanish translation (can have multiple matches)."""
        pass
    
    @abstractmethod
    async def search_similar_shuar_words(
        self, 
        shuar_text: str, 
        similarity_threshold: float = 0.5,
        limit: int = 10
    ) -> List[Word]:
        """Find Shuar words similar to the given text based on phonological similarity."""
        pass
    
    @abstractmethod
    async def search_similar_spanish_words(
        self, 
        spanish_text: str, 
        similarity_threshold: float = 0.5,
        limit: int = 10
    ) -> List[Word]:
        """Find words with similar Spanish translations."""
        pass
    
    @abstractmethod
    async def find_by_root_word(self, root_word: str) -> List[Word]:
        """Find words that share the same morphological root."""
        pass
    
    @abstractmethod
    async def find_by_vocal_types(self, vocal_types: List[VocalType]) -> List[Word]:
        """Find words containing specific vocal types."""
        pass
    
    @abstractmethod
    async def find_by_word_type(self, word_type: WordType) -> List[Word]:
        """Find words of a specific grammatical type."""
        pass
    
    @abstractmethod
    async def find_compound_words(self) -> List[Word]:
        """Find all compound words in the repository."""
        pass
    
    @abstractmethod
    async def find_words_with_suffix(self, suffix: str) -> List[Word]:
        """Find words that contain a specific suffix."""
        pass
    
    @abstractmethod
    async def find_most_frequent(self, limit: int = 100) -> List[Word]:
        """Find the most frequently used words."""
        pass
    
    @abstractmethod
    async def find_recently_added(self, limit: int = 50) -> List[Word]:
        """Find recently added words."""
        pass
    
    @abstractmethod
    async def find_unverified_words(self) -> List[Word]:
        """Find words that haven't been verified by experts."""
        pass
    
    @abstractmethod
    async def find_low_confidence_words(self, threshold: float = 0.5) -> List[Word]:
        """Find words with confidence below threshold."""
        pass
    
    @abstractmethod
    async def search_full_text(
        self, 
        query: str, 
        language: str = "both",
        limit: int = 50
    ) -> List[Word]:
        """Perform full-text search across Shuar text, Spanish translation, and definitions."""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics (total words, by type, etc.)."""
        pass
    
    @abstractmethod
    async def update(self, word: Word) -> Word:
        """Update an existing word entity."""
        pass
    
    @abstractmethod
    async def delete(self, word_id: UUID) -> bool:
        """Delete a word by its ID. Returns True if deleted, False if not found."""
        pass
    
    @abstractmethod
    async def exists(self, word_id: UUID) -> bool:
        """Check if a word exists by its ID."""
        pass
    
    @abstractmethod
    async def exists_by_shuar_text(self, shuar_text: str) -> bool:
        """Check if a word exists by its Shuar text."""
        pass
    
    @abstractmethod
    async def bulk_save(self, words: List[Word]) -> List[Word]:
        """Save multiple words in a single operation."""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Get total count of words in repository."""
        pass
    
    @abstractmethod
    async def count_by_word_type(self, word_type: WordType) -> int:
        """Get count of words by grammatical type."""
        pass
    
    @abstractmethod
    async def count_verified(self) -> int:
        """Get count of verified words."""
        pass