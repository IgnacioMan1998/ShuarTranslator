"""Feedback repository interface for domain layer."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.features.feedback.domain.entities.feedback import Feedback, FeedbackType, FeedbackStatus, UserRole


class IFeedbackRepository(ABC):
    """Interface for Feedback repository following repository pattern."""
    
    @abstractmethod
    async def save(self, feedback: Feedback) -> Feedback:
        """Save a feedback entity to the repository."""
        pass
    
    @abstractmethod
    async def find_by_id(self, feedback_id: UUID) -> Optional[Feedback]:
        """Find feedback by its unique identifier."""
        pass
    
    @abstractmethod
    async def find_by_translation_id(self, translation_id: UUID) -> List[Feedback]:
        """Find all feedback for a specific translation."""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> List[Feedback]:
        """Find all feedback submitted by a specific user."""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: FeedbackStatus) -> List[Feedback]:
        """Find feedback by approval status."""
        pass
    
    @abstractmethod
    async def find_pending_review(self) -> List[Feedback]:
        """Find feedback pending expert review."""
        pass
    
    @abstractmethod
    async def find_by_feedback_type(self, feedback_type: FeedbackType) -> List[Feedback]:
        """Find feedback by type (rating, correction, suggestion, etc.)."""
        pass
    
    @abstractmethod
    async def find_by_user_role(self, user_role: UserRole) -> List[Feedback]:
        """Find feedback by user role."""
        pass
    
    @abstractmethod
    async def find_from_native_speakers(self) -> List[Feedback]:
        """Find feedback from verified native Shuar speakers."""
        pass
    
    @abstractmethod
    async def find_high_value_feedback(self) -> List[Feedback]:
        """Find feedback considered high value (from experts, native speakers, etc.)."""
        pass
    
    @abstractmethod
    async def find_needs_expert_attention(self) -> List[Feedback]:
        """Find feedback that needs expert attention."""
        pass
    
    @abstractmethod
    async def find_by_rating_range(self, min_rating: int, max_rating: int) -> List[Feedback]:
        """Find feedback within a specific rating range."""
        pass
    
    @abstractmethod
    async def find_with_suggestions(self) -> List[Feedback]:
        """Find feedback that includes translation suggestions."""
        pass
    
    @abstractmethod
    async def find_with_cultural_notes(self) -> List[Feedback]:
        """Find feedback that includes cultural context."""
        pass
    
    @abstractmethod
    async def find_recently_submitted(
        self, 
        since: datetime, 
        limit: int = 50
    ) -> List[Feedback]:
        """Find feedback submitted since a specific date."""
        pass
    
    @abstractmethod
    async def find_reviewed_by_expert(self, expert_id: UUID) -> List[Feedback]:
        """Find feedback reviewed by a specific expert."""
        pass
    
    @abstractmethod
    async def find_approved_feedback(self) -> List[Feedback]:
        """Find all approved feedback."""
        pass
    
    @abstractmethod
    async def find_rejected_feedback(self) -> List[Feedback]:
        """Find all rejected feedback."""
        pass
    
    @abstractmethod
    async def find_implemented_feedback(self) -> List[Feedback]:
        """Find feedback that has been implemented in translations."""
        pass
    
    @abstractmethod
    async def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get comprehensive feedback statistics."""
        pass
    
    @abstractmethod
    async def get_translation_feedback_summary(
        self, 
        translation_id: UUID
    ) -> Dict[str, Any]:
        """Get feedback summary for a specific translation."""
        pass
    
    @abstractmethod
    async def get_user_feedback_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get feedback statistics for a specific user."""
        pass
    
    @abstractmethod
    async def calculate_weighted_average_rating(
        self, 
        translation_id: UUID
    ) -> Optional[float]:
        """Calculate weighted average rating for a translation based on user roles."""
        pass
    
    @abstractmethod
    async def get_feedback_trends(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get feedback trends over a date range."""
        pass
    
    @abstractmethod
    async def update(self, feedback: Feedback) -> Feedback:
        """Update an existing feedback entity."""
        pass
    
    @abstractmethod
    async def delete(self, feedback_id: UUID) -> bool:
        """Delete feedback by its ID."""
        pass
    
    @abstractmethod
    async def exists(self, feedback_id: UUID) -> bool:
        """Check if feedback exists by its ID."""
        pass
    
    @abstractmethod
    async def has_user_rated_translation(
        self, 
        user_id: UUID, 
        translation_id: UUID
    ) -> bool:
        """Check if a user has already rated a specific translation."""
        pass
    
    @abstractmethod
    async def bulk_save(self, feedback_list: List[Feedback]) -> List[Feedback]:
        """Save multiple feedback entries in a single operation."""
        pass
    
    @abstractmethod
    async def bulk_update_status(
        self, 
        feedback_ids: List[UUID], 
        status: FeedbackStatus,
        reviewed_by: UUID,
        expert_notes: Optional[str] = None
    ) -> int:
        """Bulk update status for multiple feedback entries."""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Get total count of feedback entries."""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: FeedbackStatus) -> int:
        """Get count of feedback by status."""
        pass
    
    @abstractmethod
    async def count_by_type(self, feedback_type: FeedbackType) -> int:
        """Get count of feedback by type."""
        pass
    
    @abstractmethod
    async def count_by_user_role(self, user_role: UserRole) -> int:
        """Get count of feedback by user role."""
        pass
    
    @abstractmethod
    async def count_from_native_speakers(self) -> int:
        """Get count of feedback from native speakers."""
        pass
    
    @abstractmethod
    async def get_average_rating_by_translation(
        self, 
        translation_id: UUID
    ) -> Optional[float]:
        """Get average rating for a specific translation."""
        pass
    
    @abstractmethod
    async def get_rating_distribution(self, translation_id: UUID) -> Dict[int, int]:
        """Get rating distribution (1-5 stars) for a translation."""
        pass