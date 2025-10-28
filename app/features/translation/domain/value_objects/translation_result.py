"""Value object representing the result of a translation operation."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.shared.exceptions import ValidationError
from app.features.translation.domain.entities.word import Word
from app.features.translation.domain.value_objects.similarity_score import SimilarityScore


@dataclass(frozen=True)
class SimilarWord:
    """Value object representing a similar word suggestion."""
    
    word: Word
    similarity: SimilarityScore
    explanation: Optional[str] = None
    
    def __post_init__(self):
        """Validate similar word after initialization."""
        if not isinstance(self.word, Word):
            raise ValidationError("Word must be a valid Word entity")
        
        if not isinstance(self.similarity, SimilarityScore):
            raise ValidationError("Similarity must be a valid SimilarityScore")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "word": self.word.to_dict(),
            "similarity": self.similarity.to_dict(),
            "explanation": self.explanation
        }


@dataclass(frozen=True)
class TranslationResult:
    """Value object representing the complete result of a translation request."""
    
    original_text: str
    detected_language: str
    translations: List[Dict[str, Any]]
    phonetic_info: Optional[Dict[str, Any]] = None
    morphological_analysis: Optional[Dict[str, Any]] = None
    similar_words: List[SimilarWord] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    word_count: int = 0
    
    def __post_init__(self):
        """Validate translation result after initialization."""
        if not self.original_text or not self.original_text.strip():
            raise ValidationError("Original text cannot be empty")
        
        if not self.detected_language:
            raise ValidationError("Detected language is required")
        
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
        
        if self.processing_time_ms < 0:
            raise ValidationError("Processing time cannot be negative")
        
        if self.word_count < 0:
            raise ValidationError("Word count cannot be negative")
        
        if not self.translations:
            raise ValidationError("At least one translation must be provided")
    
    @classmethod
    def create_successful(
        cls,
        original_text: str,
        detected_language: str,
        translations: List[Dict[str, Any]],
        confidence_score: float,
        processing_time_ms: int = 0,
        phonetic_info: Optional[Dict[str, Any]] = None,
        morphological_analysis: Optional[Dict[str, Any]] = None,
        similar_words: Optional[List[SimilarWord]] = None
    ) -> 'TranslationResult':
        """Create a successful translation result."""
        word_count = len(original_text.split())
        
        return cls(
            original_text=original_text,
            detected_language=detected_language,
            translations=translations,
            phonetic_info=phonetic_info,
            morphological_analysis=morphological_analysis,
            similar_words=similar_words or [],
            confidence_score=confidence_score,
            processing_time_ms=processing_time_ms,
            word_count=word_count
        )
    
    @classmethod
    def create_with_suggestions(
        cls,
        original_text: str,
        detected_language: str,
        similar_words: List[SimilarWord],
        processing_time_ms: int = 0
    ) -> 'TranslationResult':
        """Create a translation result with only similar word suggestions."""
        word_count = len(original_text.split())
        
        # Create a placeholder translation indicating no exact match
        placeholder_translation = {
            "text": f"No exact translation found for '{original_text}'",
            "confidence": 0.0,
            "type": "suggestion"
        }
        
        return cls(
            original_text=original_text,
            detected_language=detected_language,
            translations=[placeholder_translation],
            similar_words=similar_words,
            confidence_score=0.0,
            processing_time_ms=processing_time_ms,
            word_count=word_count
        )
    
    def has_exact_translation(self) -> bool:
        """Check if result contains exact translations (not just suggestions)."""
        return any(
            translation.get("confidence", 0.0) > 0.5 
            for translation in self.translations
        )
    
    def has_similar_words(self) -> bool:
        """Check if result contains similar word suggestions."""
        return len(self.similar_words) > 0
    
    def get_best_translation(self) -> Optional[Dict[str, Any]]:
        """Get the translation with highest confidence."""
        if not self.translations:
            return None
        
        return max(self.translations, key=lambda t: t.get("confidence", 0.0))
    
    def get_high_confidence_translations(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Get translations with confidence above threshold."""
        return [
            translation for translation in self.translations
            if translation.get("confidence", 0.0) >= threshold
        ]
    
    def is_high_quality(self) -> bool:
        """Check if this is a high-quality translation result."""
        return (
            self.confidence_score >= 0.7 and
            self.has_exact_translation() and
            self.processing_time_ms < 3000  # Less than 3 seconds
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_text": self.original_text,
            "detected_language": self.detected_language,
            "translations": self.translations,
            "phonetic_info": self.phonetic_info,
            "morphological_analysis": self.morphological_analysis,
            "similar_words": [sw.to_dict() for sw in self.similar_words],
            "confidence_score": self.confidence_score,
            "processing_time_ms": self.processing_time_ms,
            "word_count": self.word_count,
            "has_exact_translation": self.has_exact_translation(),
            "has_similar_words": self.has_similar_words(),
            "is_high_quality": self.is_high_quality()
        }