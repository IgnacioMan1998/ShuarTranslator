"""Translation domain entity representing a translation pair."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from app.core.shared.exceptions import ValidationError
from app.features.translation.domain.entities.word import Word


class Language(Enum):
    """Supported languages for translation."""
    SHUAR = "shuar"
    SPANISH = "spanish"


class TranslationStatus(Enum):
    """Status of a translation."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


@dataclass
class TranslationContext:
    """Context information for a translation."""
    domain: Optional[str] = None  # e.g., "ceremonial", "daily", "hunting"
    register: Optional[str] = None  # e.g., "formal", "informal", "archaic"
    dialect: Optional[str] = None  # e.g., "northern", "southern"
    cultural_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "domain": self.domain,
            "register": self.register,
            "dialect": self.dialect,
            "cultural_notes": self.cultural_notes
        }


@dataclass
class Translation:
    """Domain entity representing a translation between Shuar and Spanish."""
    
    id: UUID = field(default_factory=uuid4)
    source_text: str = ""
    target_text: str = ""
    source_language: Language = Language.SHUAR
    target_language: Language = Language.SPANISH
    confidence_score: float = 0.5
    context: Optional[TranslationContext] = None
    word_references: List[UUID] = field(default_factory=list)  # References to Word entities
    usage_count: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0
    status: TranslationStatus = TranslationStatus.PENDING
    created_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate translation entity after initialization."""
        self._validate_required_fields()
        self._validate_languages()
        self._validate_confidence_score()
        self._validate_rating()
    
    def _validate_required_fields(self):
        """Validate that required fields are present."""
        if not self.source_text or not self.source_text.strip():
            raise ValidationError("Source text is required")
        
        if not self.target_text or not self.target_text.strip():
            raise ValidationError("Target text is required")
    
    def _validate_languages(self):
        """Validate that source and target languages are different."""
        if self.source_language == self.target_language:
            raise ValidationError("Source and target languages must be different")
    
    def _validate_confidence_score(self):
        """Validate confidence score is within valid range."""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
    
    def _validate_rating(self):
        """Validate rating values."""
        if not 0.0 <= self.average_rating <= 5.0:
            raise ValidationError("Average rating must be between 0.0 and 5.0")
        
        if self.total_ratings < 0:
            raise ValidationError("Total ratings cannot be negative")
    
    def update_translation(self, new_target_text: str, updated_by: Optional[UUID] = None) -> None:
        """Update the target translation text."""
        if not new_target_text or not new_target_text.strip():
            raise ValidationError("Target text cannot be empty")
        
        self.target_text = new_target_text.strip()
        self.status = TranslationStatus.NEEDS_REVIEW
        self.updated_at = datetime.now()
        
        # Reset approval if translation is updated
        self.approved_by = None
        self.approved_at = None
    
    def add_word_reference(self, word_id: UUID) -> None:
        """Add a reference to a Word entity."""
        if word_id not in self.word_references:
            self.word_references.append(word_id)
            self.updated_at = datetime.now()
    
    def remove_word_reference(self, word_id: UUID) -> None:
        """Remove a reference to a Word entity."""
        if word_id in self.word_references:
            self.word_references.remove(word_id)
            self.updated_at = datetime.now()
    
    def increment_usage(self) -> None:
        """Increment usage count when translation is used."""
        self.usage_count += 1
        self.updated_at = datetime.now()
    
    def add_rating(self, rating: int) -> None:
        """Add a new rating and recalculate average."""
        if not 1 <= rating <= 5:
            raise ValidationError("Rating must be between 1 and 5")
        
        # Calculate new average rating
        total_score = self.average_rating * self.total_ratings + rating
        self.total_ratings += 1
        self.average_rating = total_score / self.total_ratings
        
        self.updated_at = datetime.now()
    
    def update_confidence(self, new_confidence: float) -> None:
        """Update confidence score."""
        if not 0.0 <= new_confidence <= 1.0:
            raise ValidationError("Confidence score must be between 0.0 and 1.0")
        
        self.confidence_score = new_confidence
        self.updated_at = datetime.now()
    
    def approve(self, approved_by: UUID) -> None:
        """Approve the translation."""
        self.status = TranslationStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = datetime.now()
        self.updated_at = datetime.now()
    
    def reject(self) -> None:
        """Reject the translation."""
        self.status = TranslationStatus.REJECTED
        self.approved_by = None
        self.approved_at = None
        self.updated_at = datetime.now()
    
    def mark_needs_review(self) -> None:
        """Mark translation as needing review."""
        self.status = TranslationStatus.NEEDS_REVIEW
        self.updated_at = datetime.now()
    
    def set_context(self, context: TranslationContext) -> None:
        """Set translation context information."""
        self.context = context
        self.updated_at = datetime.now()
    
    def is_bidirectional_pair(self, other: 'Translation') -> bool:
        """Check if this translation forms a bidirectional pair with another."""
        return (
            self.source_text.lower().strip() == other.target_text.lower().strip() and
            self.target_text.lower().strip() == other.source_text.lower().strip() and
            self.source_language == other.target_language and
            self.target_language == other.source_language
        )
    
    def get_reverse_translation(self) -> 'Translation':
        """Create a reverse translation (swap source and target)."""
        return Translation(
            source_text=self.target_text,
            target_text=self.source_text,
            source_language=self.target_language,
            target_language=self.source_language,
            confidence_score=self.confidence_score,
            context=self.context,
            word_references=self.word_references.copy(),
            created_by=self.created_by
        )
    
    def is_high_quality(self) -> bool:
        """Determine if translation is high quality based on ratings and approval."""
        return (
            self.status == TranslationStatus.APPROVED and
            self.average_rating >= 4.0 and
            self.total_ratings >= 3
        )
    
    def needs_community_review(self) -> bool:
        """Determine if translation needs community review."""
        return (
            self.status in [TranslationStatus.PENDING, TranslationStatus.NEEDS_REVIEW] or
            (self.average_rating < 3.0 and self.total_ratings >= 5)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert translation entity to dictionary representation."""
        return {
            "id": str(self.id),
            "source_text": self.source_text,
            "target_text": self.target_text,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value,
            "confidence_score": self.confidence_score,
            "context": self.context.to_dict() if self.context else None,
            "word_references": [str(ref) for ref in self.word_references],
            "usage_count": self.usage_count,
            "average_rating": self.average_rating,
            "total_ratings": self.total_ratings,
            "status": self.status.value,
            "created_by": str(self.created_by) if self.created_by else None,
            "approved_by": str(self.approved_by) if self.approved_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None
        }