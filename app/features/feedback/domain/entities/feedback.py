"""Feedback domain entity representing community feedback on translations."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from app.core.shared.exceptions import ValidationError


class FeedbackType(Enum):
    """Types of feedback that can be provided."""
    RATING = "rating"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"
    CULTURAL_NOTE = "cultural_note"
    PRONUNCIATION = "pronunciation"


class FeedbackStatus(Enum):
    """Status of feedback submission."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class UserRole(Enum):
    """Roles of users providing feedback."""
    VISITOR = "visitor"
    COMMUNITY_MEMBER = "community_member"
    VERIFIED_SPEAKER = "verified_speaker"
    EXPERT = "expert"
    ADMIN = "admin"


@dataclass
class Feedback:
    """Domain entity representing community feedback on translations."""
    
    id: UUID = field(default_factory=uuid4)
    translation_id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    user_role: UserRole = UserRole.VISITOR
    feedback_type: FeedbackType = FeedbackType.RATING
    rating: Optional[int] = None
    comment: Optional[str] = None
    suggested_translation: Optional[str] = None
    cultural_context: Optional[str] = None
    pronunciation_notes: Optional[str] = None
    is_from_native_speaker: bool = False
    status: FeedbackStatus = FeedbackStatus.PENDING
    expert_notes: Optional[str] = None
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate feedback entity after initialization."""
        self._validate_feedback_content()
        self._validate_rating()
        self._validate_text_lengths()
    
    def _validate_feedback_content(self):
        """Validate that feedback has meaningful content."""
        has_rating = self.rating is not None
        has_comment = self.comment and self.comment.strip()
        has_suggestion = self.suggested_translation and self.suggested_translation.strip()
        has_cultural_context = self.cultural_context and self.cultural_context.strip()
        has_pronunciation = self.pronunciation_notes and self.pronunciation_notes.strip()
        
        if not any([has_rating, has_comment, has_suggestion, has_cultural_context, has_pronunciation]):
            raise ValidationError("Feedback must contain at least one form of content")
    
    def _validate_rating(self):
        """Validate rating value if provided."""
        if self.rating is not None:
            if not isinstance(self.rating, int) or not 1 <= self.rating <= 5:
                raise ValidationError("Rating must be an integer between 1 and 5")
    
    def _validate_text_lengths(self):
        """Validate text field lengths."""
        max_lengths = {
            'comment': 1000,
            'suggested_translation': 500,
            'cultural_context': 1000,
            'pronunciation_notes': 500,
            'expert_notes': 1000
        }
        
        for field_name, max_length in max_lengths.items():
            value = getattr(self, field_name)
            if value and len(value) > max_length:
                raise ValidationError(f"{field_name} exceeds maximum length of {max_length} characters")
    
    def update_rating(self, new_rating: int) -> None:
        """Update the rating value."""
        if not isinstance(new_rating, int) or not 1 <= new_rating <= 5:
            raise ValidationError("Rating must be an integer between 1 and 5")
        
        self.rating = new_rating
        self.feedback_type = FeedbackType.RATING
        self.updated_at = datetime.now()
    
    def update_comment(self, new_comment: str) -> None:
        """Update the comment."""
        if len(new_comment) > 1000:
            raise ValidationError("Comment exceeds maximum length of 1000 characters")
        
        self.comment = new_comment.strip() if new_comment else None
        self.updated_at = datetime.now()
    
    def update_suggestion(self, new_suggestion: str) -> None:
        """Update the suggested translation."""
        if not new_suggestion or not new_suggestion.strip():
            raise ValidationError("Suggested translation cannot be empty")
        
        if len(new_suggestion) > 500:
            raise ValidationError("Suggested translation exceeds maximum length of 500 characters")
        
        self.suggested_translation = new_suggestion.strip()
        self.feedback_type = FeedbackType.SUGGESTION
        self.updated_at = datetime.now()
    
    def add_cultural_context(self, cultural_context: str) -> None:
        """Add cultural context information."""
        if len(cultural_context) > 1000:
            raise ValidationError("Cultural context exceeds maximum length of 1000 characters")
        
        self.cultural_context = cultural_context.strip()
        self.feedback_type = FeedbackType.CULTURAL_NOTE
        self.updated_at = datetime.now()
    
    def add_pronunciation_notes(self, pronunciation_notes: str) -> None:
        """Add pronunciation notes."""
        if len(pronunciation_notes) > 500:
            raise ValidationError("Pronunciation notes exceed maximum length of 500 characters")
        
        self.pronunciation_notes = pronunciation_notes.strip()
        self.feedback_type = FeedbackType.PRONUNCIATION
        self.updated_at = datetime.now()
    
    def mark_as_native_speaker(self) -> None:
        """Mark feedback as coming from a native Shuar speaker."""
        self.is_from_native_speaker = True
        self.updated_at = datetime.now()
    
    def review(self, reviewed_by: UUID, expert_notes: Optional[str] = None) -> None:
        """Mark feedback as reviewed by an expert."""
        self.status = FeedbackStatus.REVIEWED
        self.reviewed_by = reviewed_by
        self.reviewed_at = datetime.now()
        self.updated_at = datetime.now()
        
        if expert_notes:
            if len(expert_notes) > 1000:
                raise ValidationError("Expert notes exceed maximum length of 1000 characters")
            self.expert_notes = expert_notes.strip()
    
    def approve(self, approved_by: UUID, expert_notes: Optional[str] = None) -> None:
        """Approve the feedback."""
        self.status = FeedbackStatus.APPROVED
        self.reviewed_by = approved_by
        self.reviewed_at = datetime.now()
        self.updated_at = datetime.now()
        
        if expert_notes:
            if len(expert_notes) > 1000:
                raise ValidationError("Expert notes exceed maximum length of 1000 characters")
            self.expert_notes = expert_notes.strip()
    
    def reject(self, rejected_by: UUID, expert_notes: str) -> None:
        """Reject the feedback with explanation."""
        if not expert_notes or not expert_notes.strip():
            raise ValidationError("Expert notes are required when rejecting feedback")
        
        if len(expert_notes) > 1000:
            raise ValidationError("Expert notes exceed maximum length of 1000 characters")
        
        self.status = FeedbackStatus.REJECTED
        self.reviewed_by = rejected_by
        self.reviewed_at = datetime.now()
        self.expert_notes = expert_notes.strip()
        self.updated_at = datetime.now()
    
    def implement(self) -> None:
        """Mark feedback as implemented in the translation."""
        if self.status != FeedbackStatus.APPROVED:
            raise ValidationError("Only approved feedback can be marked as implemented")
        
        self.status = FeedbackStatus.IMPLEMENTED
        self.updated_at = datetime.now()
    
    def is_high_value(self) -> bool:
        """Determine if feedback is high value based on user role and content."""
        high_value_roles = [UserRole.VERIFIED_SPEAKER, UserRole.EXPERT, UserRole.ADMIN]
        
        return (
            self.user_role in high_value_roles or
            self.is_from_native_speaker or
            (self.rating is not None and self.rating in [1, 5]) or  # Extreme ratings
            (self.suggested_translation is not None and len(self.suggested_translation) > 10) or
            (self.cultural_context is not None and len(self.cultural_context) > 20)
        )
    
    def needs_expert_attention(self) -> bool:
        """Determine if feedback needs expert attention."""
        return (
            self.feedback_type in [FeedbackType.CORRECTION, FeedbackType.CULTURAL_NOTE] or
            (self.rating is not None and self.rating <= 2) or  # Low ratings
            self.is_from_native_speaker or
            self.user_role in [UserRole.VERIFIED_SPEAKER, UserRole.EXPERT]
        )
    
    def get_weight(self) -> float:
        """Get the weight of this feedback for calculating averages."""
        role_weights = {
            UserRole.VISITOR: 1.0,
            UserRole.COMMUNITY_MEMBER: 1.2,
            UserRole.VERIFIED_SPEAKER: 2.0,
            UserRole.EXPERT: 3.0,
            UserRole.ADMIN: 3.0
        }
        
        base_weight = role_weights.get(self.user_role, 1.0)
        
        # Increase weight for native speakers
        if self.is_from_native_speaker:
            base_weight *= 1.5
        
        return base_weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback entity to dictionary representation."""
        return {
            "id": str(self.id),
            "translation_id": str(self.translation_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "user_role": self.user_role.value,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "comment": self.comment,
            "suggested_translation": self.suggested_translation,
            "cultural_context": self.cultural_context,
            "pronunciation_notes": self.pronunciation_notes,
            "is_from_native_speaker": self.is_from_native_speaker,
            "status": self.status.value,
            "expert_notes": self.expert_notes,
            "reviewed_by": str(self.reviewed_by) if self.reviewed_by else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }