"""Phonological repository interface for accessing Shuar phonological data."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.features.translation.domain.entities.word import VocalType


class IPhonologicalRepository(ABC):
    """Interface for accessing Shuar phonological system data."""
    
    @abstractmethod
    async def get_vocal_types(self) -> List[Dict[str, Any]]:
        """Get all vocal types (oral, nasal, laryngealized) with their properties."""
        pass
    
    @abstractmethod
    async def get_vowels_by_type(self, vocal_type: VocalType) -> List[Dict[str, Any]]:
        """Get vowels of a specific type."""
        pass
    
    @abstractmethod
    async def get_all_vowels(self) -> List[Dict[str, Any]]:
        """Get all Shuar vowels with their phonological information."""
        pass
    
    @abstractmethod
    async def get_all_consonants(self) -> List[Dict[str, Any]]:
        """Get all Shuar consonants with their phonological information."""
        pass
    
    @abstractmethod
    async def get_alphabet(self) -> List[Dict[str, Any]]:
        """Get the complete Shuar alphabet in order."""
        pass
    
    @abstractmethod
    async def get_consonants_by_articulation(
        self, 
        point_of_articulation: str
    ) -> List[Dict[str, Any]]:
        """Get consonants by point of articulation (bilabial, dental, etc.)."""
        pass
    
    @abstractmethod
    async def get_consonants_by_manner(
        self, 
        manner_of_articulation: str
    ) -> List[Dict[str, Any]]:
        """Get consonants by manner of articulation (oclusiva, fricativa, etc.)."""
        pass
    
    @abstractmethod
    async def find_letter_by_ipa(self, ipa_symbol: str) -> Optional[Dict[str, Any]]:
        """Find Shuar letter by its IPA transcription."""
        pass
    
    @abstractmethod
    async def get_digraphs(self) -> List[Dict[str, Any]]:
        """Get Shuar digraphs (ch, sh, ts)."""
        pass
    
    @abstractmethod
    async def is_valid_shuar_character(self, character: str) -> bool:
        """Check if a character is valid in the Shuar alphabet."""
        pass
    
    @abstractmethod
    async def analyze_phonological_features(self, text: str) -> Dict[str, Any]:
        """Analyze phonological features of Shuar text."""
        pass
    
    @abstractmethod
    async def get_syllable_patterns(self) -> List[str]:
        """Get common syllable patterns in Shuar."""
        pass
    
    @abstractmethod
    async def count_syllables(self, shuar_word: str) -> int:
        """Count syllables in a Shuar word."""
        pass
    
    @abstractmethod
    async def get_phonological_statistics(self) -> Dict[str, Any]:
        """Get statistics about phonological usage in the database."""
        pass