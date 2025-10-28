"""Use case for submitting feedback on translations."""

from typing import Optional
from dataclasses import dataclass
from uuid import UUID

from app.features.feedback.domain.entities.feedback import Feedback, FeedbackType, UserRole
from app.features.translation.domain.entities.translation import Translation
from app.core.shared.repositories import IFeedbackRepository, ITranslationRepository
from app.core.shared.exceptions import ValidationError, NotFoundError
from app.core.utils.validators import validate_rating, validate_comment


@dataclass
class SubmitFeedbackRequest:
    """Request for submitting feedback on a translation."""
    translation_id: UUID
    user_id: Optional[UUID] = None
    user_role: str = "visitor"  # "visitor", "community_member", "verified_speaker", "expert"
    rating: Optional[int] = None
    comment: Optional[str] = None
    suggested_translation: Optional[str] = None
    cultural_context: Optional[str] = None
    pronunciation_notes: Optional[str] = None
    is_from_native_speaker: bool = False


class SubmitFeedbackUseCase:
    """Use case for submitting feedback on translations."""
    
    def __init__(
        self,
        feedback_repository: IFeedbackRepository,
        translation_repository: ITranslationRepository
    ):
        self.feedback_repository = feedback_repository
        self.translation_repository = translation_repository
    
    async def execute(self, request: SubmitFeedbackRequest) -> Feedback:
        """Execute the submit feedback use case."""
        # Validate request
        await self._validate_request(request)
        
        # Check if user has already provided feedback for this translation
        if request.user_id:
            existing_feedback = await self.feedback_repository.has_user_rated_translation(
                request.user_id, request.translation_id
            )
            if existing_feedback:
                raise ValidationError("User has already provided feedback for this translation")
        
        # Determine feedback type based on content
        feedback_type = self._determine_feedback_type(request)
        
        # Create feedback entity
        feedback = Feedback(
            translation_id=request.translation_id,
            user_id=request.user_id,
            user_role=UserRole(request.user_role.lower()),
            feedback_type=feedback_type,
            rating=request.rating,
            comment=validate_comment(request.comment) if request.comment else None,
            suggested_translation=request.suggested_translation.strip() if request.suggested_translation else None,
            cultural_context=request.cultural_context.strip() if request.cultural_context else None,
            pronunciation_notes=request.pronunciation_notes.strip() if request.pronunciation_notes else None,
            is_from_native_speaker=request.is_from_native_speaker
        )
        
        # Save feedback
        saved_feedback = await self.feedback_repository.save(feedback)
        
        # Update translation rating if rating was provided
        if request.rating:
            await self._update_translation_rating(request.translation_id, request.rating)
        
        return saved_feedback
    
    async def _validate_request(self, request: SubmitFeedbackRequest) -> None:
        """Validate the feedback request."""
        # Check if translation exists
        translation = await self.translation_repository.find_by_id(request.translation_id)
        if not translation:
            raise NotFoundError(f"Translation with ID {request.translation_id} not found")
        
        # Validate user role
        valid_roles = {"visitor", "community_member", "verified_speaker", "expert", "admin"}
        if request.user_role.lower() not in valid_roles:
            raise ValidationError(f"Invalid user role: {request.user_role}")
        
        # Validate rating if provided
        if request.rating is not None:
            validate_rating(request.rating)
        
        # Validate that at least one form of feedback is provided
        has_content = any([
            request.rating is not None,
            request.comment and request.comment.strip(),
            request.suggested_translation and request.suggested_translation.strip(),
            request.cultural_context and request.cultural_context.strip(),
            request.pronunciation_notes and request.pronunciation_notes.strip()
        ])
        
        if not has_content:
            raise ValidationError("At least one form of feedback must be provided")
        
        # Validate text lengths
        if request.comment and len(request.comment) > 1000:
            raise ValidationError("Comment exceeds maximum length of 1000 characters")
        
        if request.suggested_translation and len(request.suggested_translation) > 500:
            raise ValidationError("Suggested translation exceeds maximum length of 500 characters")
        
        if request.cultural_context and len(request.cultural_context) > 1000:
            raise ValidationError("Cultural context exceeds maximum length of 1000 characters")
        
        if request.pronunciation_notes and len(request.pronunciation_notes) > 500:
            raise ValidationError("Pronunciation notes exceed maximum length of 500 characters")
    
    def _determine_feedback_type(self, request: SubmitFeedbackRequest) -> FeedbackType:
        """Determine the primary feedback type based on content."""
        if request.suggested_translation and request.suggested_translation.strip():
            return FeedbackType.SUGGESTION
        elif request.cultural_context and request.cultural_context.strip():
            return FeedbackType.CULTURAL_NOTE
        elif request.pronunciation_notes and request.pronunciation_notes.strip():
            return FeedbackType.PRONUNCIATION
        elif request.rating is not None:
            return FeedbackType.RATING
        else:
            return FeedbackType.RATING  # Default
    
    async def _update_translation_rating(self, translation_id: UUID, rating: int) -> None:
        """Update the translation's average rating."""
        try:
            translation = await self.translation_repository.find_by_id(translation_id)
            if translation:
                translation.add_rating(rating)
                await self.translation_repository.update(translation)
        except Exception:
            # Don't fail the feedback submission if rating update fails
            pass


@dataclass
class GetTranslationFeedbackRequest:
    """Request for getting feedback for a translation."""
    translation_id: UUID
    include_pending: bool = True
    include_rejected: bool = False
    limit: int = 50
    offset: int = 0


class GetTranslationFeedbackUseCase:
    """Use case for retrieving feedback for a specific translation."""
    
    def __init__(self, feedback_repository: IFeedbackRepository):
        self.feedback_repository = feedback_repository
    
    async def execute(self, request: GetTranslationFeedbackRequest) -> dict:
        """Execute the get translation feedback use case."""
        # Get all feedback for the translation
        all_feedback = await self.feedback_repository.find_by_translation_id(
            request.translation_id
        )
        
        # Filter feedback based on request parameters
        filtered_feedback = self._filter_feedback(all_feedback, request)
        
        # Apply pagination
        paginated_feedback = filtered_feedback[request.offset:request.offset + request.limit]
        
        # Calculate summary statistics
        summary = self._calculate_feedback_summary(all_feedback)
        
        return {
            "feedback": [feedback.to_dict() for feedback in paginated_feedback],
            "total_count": len(filtered_feedback),
            "summary": summary
        }
    
    def _filter_feedback(self, feedback_list: list, request: GetTranslationFeedbackRequest) -> list:
        """Filter feedback based on request parameters."""
        filtered = []
        
        for feedback in feedback_list:
            # Include based on status
            if feedback.status.value == "pending" and not request.include_pending:
                continue
            if feedback.status.value == "rejected" and not request.include_rejected:
                continue
            
            filtered.append(feedback)
        
        # Sort by creation date (newest first)
        filtered.sort(key=lambda f: f.created_at, reverse=True)
        
        return filtered
    
    def _calculate_feedback_summary(self, feedback_list: list) -> dict:
        """Calculate summary statistics for feedback."""
        if not feedback_list:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_distribution": {},
                "feedback_types": {},
                "native_speaker_count": 0,
                "expert_feedback_count": 0
            }
        
        # Calculate rating statistics
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Rating distribution
        rating_distribution = {}
        for rating in ratings:
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        # Feedback types
        feedback_types = {}
        for feedback in feedback_list:
            feedback_type = feedback.feedback_type.value
            feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
        
        # Special counts
        native_speaker_count = sum(1 for f in feedback_list if f.is_from_native_speaker)
        expert_feedback_count = sum(
            1 for f in feedback_list 
            if f.user_role.value in ["expert", "admin"]
        )
        
        return {
            "total_feedback": len(feedback_list),
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "feedback_types": feedback_types,
            "native_speaker_count": native_speaker_count,
            "expert_feedback_count": expert_feedback_count
        }


@dataclass
class SuggestAlternativeTranslationRequest:
    """Request for suggesting an alternative translation."""
    translation_id: UUID
    user_id: Optional[UUID] = None
    user_role: str = "community_member"
    suggested_translation: str = ""
    explanation: Optional[str] = None
    cultural_context: Optional[str] = None
    is_from_native_speaker: bool = False


class SuggestAlternativeTranslationUseCase:
    """Use case for community members to suggest alternative translations."""
    
    def __init__(
        self,
        feedback_repository: IFeedbackRepository,
        translation_repository: ITranslationRepository
    ):
        self.feedback_repository = feedback_repository
        self.translation_repository = translation_repository
    
    async def execute(self, request: SuggestAlternativeTranslationRequest) -> Feedback:
        """Execute the suggest alternative translation use case."""
        # Validate request
        await self._validate_request(request)
        
        # Create feedback with suggestion
        feedback = Feedback(
            translation_id=request.translation_id,
            user_id=request.user_id,
            user_role=UserRole(request.user_role.lower()),
            feedback_type=FeedbackType.SUGGESTION,
            suggested_translation=request.suggested_translation.strip(),
            comment=request.explanation.strip() if request.explanation else None,
            cultural_context=request.cultural_context.strip() if request.cultural_context else None,
            is_from_native_speaker=request.is_from_native_speaker
        )
        
        # Save feedback
        saved_feedback = await self.feedback_repository.save(feedback)
        
        return saved_feedback
    
    async def _validate_request(self, request: SuggestAlternativeTranslationRequest) -> None:
        """Validate the suggestion request."""
        # Check if translation exists
        translation = await self.translation_repository.find_by_id(request.translation_id)
        if not translation:
            raise NotFoundError(f"Translation with ID {request.translation_id} not found")
        
        # Validate suggested translation
        if not request.suggested_translation or not request.suggested_translation.strip():
            raise ValidationError("Suggested translation cannot be empty")
        
        if len(request.suggested_translation) > 500:
            raise ValidationError("Suggested translation exceeds maximum length of 500 characters")
        
        # Validate user role
        valid_roles = {"community_member", "verified_speaker", "expert", "admin"}
        if request.user_role.lower() not in valid_roles:
            raise ValidationError(f"Invalid user role for suggestions: {request.user_role}")
        
        # Validate optional fields
        if request.explanation and len(request.explanation) > 1000:
            raise ValidationError("Explanation exceeds maximum length of 1000 characters")
        
        if request.cultural_context and len(request.cultural_context) > 1000:
            raise ValidationError("Cultural context exceeds maximum length of 1000 characters")