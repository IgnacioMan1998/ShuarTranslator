"""Use case for experts to review and approve community feedback."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from uuid import UUID

from app.features.feedback.domain.entities.feedback import Feedback, FeedbackStatus
from app.features.translation.domain.entities.translation import Translation
from app.core.shared.repositories import IFeedbackRepository, ITranslationRepository
from app.core.shared.exceptions import ValidationError, NotFoundError


@dataclass
class ReviewFeedbackRequest:
    """Request for reviewing feedback."""
    feedback_id: UUID
    expert_id: UUID
    action: str  # "approve", "reject", "implement"
    expert_notes: Optional[str] = None


class ReviewFeedbackUseCase:
    """Use case for experts to review community feedback."""
    
    def __init__(
        self,
        feedback_repository: IFeedbackRepository,
        translation_repository: ITranslationRepository
    ):
        self.feedback_repository = feedback_repository
        self.translation_repository = translation_repository
    
    async def execute(self, request: ReviewFeedbackRequest) -> Feedback:
        """Execute the review feedback use case."""
        # Validate request
        self._validate_request(request)
        
        # Get feedback
        feedback = await self.feedback_repository.find_by_id(request.feedback_id)
        if not feedback:
            raise NotFoundError(f"Feedback with ID {request.feedback_id} not found")
        
        # Perform action based on request
        if request.action == "approve":
            feedback.approve(request.expert_id, request.expert_notes)
        elif request.action == "reject":
            if not request.expert_notes:
                raise ValidationError("Expert notes are required when rejecting feedback")
            feedback.reject(request.expert_id, request.expert_notes)
        elif request.action == "implement":
            await self._implement_feedback(feedback, request.expert_id)
        else:
            raise ValidationError(f"Invalid action: {request.action}")
        
        # Save updated feedback
        updated_feedback = await self.feedback_repository.update(feedback)
        
        return updated_feedback
    
    def _validate_request(self, request: ReviewFeedbackRequest) -> None:
        """Validate the review request."""
        valid_actions = {"approve", "reject", "implement"}
        if request.action not in valid_actions:
            raise ValidationError(f"Invalid action. Must be one of: {', '.join(valid_actions)}")
        
        if request.action == "reject" and not request.expert_notes:
            raise ValidationError("Expert notes are required when rejecting feedback")
        
        if request.expert_notes and len(request.expert_notes) > 1000:
            raise ValidationError("Expert notes exceed maximum length of 1000 characters")
    
    async def _implement_feedback(self, feedback: Feedback, expert_id: UUID) -> None:
        """Implement approved feedback by updating the translation."""
        if feedback.status != FeedbackStatus.APPROVED:
            feedback.approve(expert_id)
        
        # If feedback has a suggested translation, create or update translation
        if feedback.suggested_translation:
            translation = await self.translation_repository.find_by_id(feedback.translation_id)
            if translation:
                # Update existing translation
                translation.update_translation(feedback.suggested_translation, expert_id)
                await self.translation_repository.update(translation)
        
        # Mark feedback as implemented
        feedback.implement()


@dataclass
class GetPendingFeedbackRequest:
    """Request for getting pending feedback for review."""
    expert_id: UUID
    feedback_types: Optional[List[str]] = None  # Filter by feedback types
    priority_only: bool = False  # Only high-priority feedback
    limit: int = 50
    offset: int = 0


class GetPendingFeedbackUseCase:
    """Use case for getting feedback that needs expert review."""
    
    def __init__(self, feedback_repository: IFeedbackRepository):
        self.feedback_repository = feedback_repository
    
    async def execute(self, request: GetPendingFeedbackRequest) -> Dict[str, Any]:
        """Execute the get pending feedback use case."""
        # Get all pending feedback
        pending_feedback = await self.feedback_repository.find_pending_review()
        
        # Filter by feedback types if specified
        if request.feedback_types:
            from app.features.feedback.domain.entities.feedback import FeedbackType
            valid_types = [FeedbackType(ft.lower()) for ft in request.feedback_types]
            pending_feedback = [
                f for f in pending_feedback 
                if f.feedback_type in valid_types
            ]
        
        # Filter by priority if requested
        if request.priority_only:
            pending_feedback = [
                f for f in pending_feedback 
                if f.needs_expert_attention()
            ]
        
        # Sort by priority and creation date
        pending_feedback.sort(
            key=lambda f: (
                f.is_high_value(),  # High value feedback first
                f.needs_expert_attention(),  # Needs attention second
                f.created_at  # Then by creation date
            ),
            reverse=True
        )
        
        # Apply pagination
        total_count = len(pending_feedback)
        paginated_feedback = pending_feedback[request.offset:request.offset + request.limit]
        
        # Format response
        return {
            "feedback": [self._format_feedback_for_review(f) for f in paginated_feedback],
            "total_count": total_count,
            "high_priority_count": sum(1 for f in pending_feedback if f.needs_expert_attention()),
            "native_speaker_count": sum(1 for f in pending_feedback if f.is_from_native_speaker)
        }
    
    def _format_feedback_for_review(self, feedback: Feedback) -> Dict[str, Any]:
        """Format feedback for expert review."""
        return {
            "id": str(feedback.id),
            "translation_id": str(feedback.translation_id),
            "feedback_type": feedback.feedback_type.value,
            "user_role": feedback.user_role.value,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "suggested_translation": feedback.suggested_translation,
            "cultural_context": feedback.cultural_context,
            "pronunciation_notes": feedback.pronunciation_notes,
            "is_from_native_speaker": feedback.is_from_native_speaker,
            "is_high_value": feedback.is_high_value(),
            "needs_expert_attention": feedback.needs_expert_attention(),
            "created_at": feedback.created_at.isoformat(),
            "weight": feedback.get_weight()
        }


@dataclass
class BulkReviewFeedbackRequest:
    """Request for bulk reviewing multiple feedback items."""
    feedback_ids: List[UUID]
    expert_id: UUID
    action: str  # "approve", "reject"
    expert_notes: Optional[str] = None


class BulkReviewFeedbackUseCase:
    """Use case for bulk reviewing multiple feedback items."""
    
    def __init__(self, feedback_repository: IFeedbackRepository):
        self.feedback_repository = feedback_repository
    
    async def execute(self, request: BulkReviewFeedbackRequest) -> Dict[str, Any]:
        """Execute the bulk review feedback use case."""
        # Validate request
        self._validate_request(request)
        
        results = {
            "total_processed": len(request.feedback_ids),
            "successful_reviews": 0,
            "failed_reviews": 0,
            "errors": []
        }
        
        # Process each feedback item
        for feedback_id in request.feedback_ids:
            try:
                feedback = await self.feedback_repository.find_by_id(feedback_id)
                if not feedback:
                    results["failed_reviews"] += 1
                    results["errors"].append({
                        "feedback_id": str(feedback_id),
                        "error": "Feedback not found"
                    })
                    continue
                
                # Apply action
                if request.action == "approve":
                    feedback.approve(request.expert_id, request.expert_notes)
                elif request.action == "reject":
                    feedback.reject(request.expert_id, request.expert_notes)
                
                # Save updated feedback
                await self.feedback_repository.update(feedback)
                results["successful_reviews"] += 1
                
            except Exception as e:
                results["failed_reviews"] += 1
                results["errors"].append({
                    "feedback_id": str(feedback_id),
                    "error": str(e)
                })
        
        return results
    
    def _validate_request(self, request: BulkReviewFeedbackRequest) -> None:
        """Validate the bulk review request."""
        if not request.feedback_ids:
            raise ValidationError("At least one feedback ID must be provided")
        
        if len(request.feedback_ids) > 100:
            raise ValidationError("Cannot process more than 100 feedback items at once")
        
        valid_actions = {"approve", "reject"}
        if request.action not in valid_actions:
            raise ValidationError(f"Invalid action. Must be one of: {', '.join(valid_actions)}")
        
        if request.action == "reject" and not request.expert_notes:
            raise ValidationError("Expert notes are required when rejecting feedback")


@dataclass
class GetFeedbackAnalyticsRequest:
    """Request for getting feedback analytics."""
    expert_id: UUID
    start_date: Optional[str] = None  # ISO format date
    end_date: Optional[str] = None
    include_user_metrics: bool = True


class GetFeedbackAnalyticsUseCase:
    """Use case for getting feedback analytics for experts."""
    
    def __init__(self, feedback_repository: IFeedbackRepository):
        self.feedback_repository = feedback_repository
    
    async def execute(self, request: GetFeedbackAnalyticsRequest) -> Dict[str, Any]:
        """Execute the get feedback analytics use case."""
        # Get comprehensive feedback statistics
        overall_stats = await self.feedback_repository.get_feedback_statistics()
        
        # Get expert-specific statistics
        expert_feedback = await self.feedback_repository.find_reviewed_by_expert(request.expert_id)
        
        # Calculate expert metrics
        expert_metrics = self._calculate_expert_metrics(expert_feedback)
        
        # Get trending feedback if date range specified
        trending_data = None
        if request.start_date and request.end_date:
            from datetime import datetime
            start_dt = datetime.fromisoformat(request.start_date)
            end_dt = datetime.fromisoformat(request.end_date)
            trending_data = await self.feedback_repository.get_feedback_trends(start_dt, end_dt)
        
        return {
            "overall_statistics": overall_stats,
            "expert_metrics": expert_metrics,
            "trending_data": trending_data,
            "summary": {
                "total_feedback_reviewed": len(expert_feedback),
                "approval_rate": expert_metrics.get("approval_rate", 0.0),
                "average_review_time": expert_metrics.get("average_review_time", 0.0)
            }
        }
    
    def _calculate_expert_metrics(self, expert_feedback: List[Feedback]) -> Dict[str, Any]:
        """Calculate metrics for expert's review activity."""
        if not expert_feedback:
            return {
                "total_reviewed": 0,
                "approved_count": 0,
                "rejected_count": 0,
                "approval_rate": 0.0
            }
        
        approved_count = sum(1 for f in expert_feedback if f.status == FeedbackStatus.APPROVED)
        rejected_count = sum(1 for f in expert_feedback if f.status == FeedbackStatus.REJECTED)
        
        return {
            "total_reviewed": len(expert_feedback),
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "approval_rate": approved_count / len(expert_feedback) if expert_feedback else 0.0,
            "feedback_types_reviewed": self._count_feedback_types(expert_feedback),
            "native_speaker_feedback_reviewed": sum(
                1 for f in expert_feedback if f.is_from_native_speaker
            )
        }
    
    def _count_feedback_types(self, feedback_list: List[Feedback]) -> Dict[str, int]:
        """Count feedback by type."""
        type_counts = {}
        for feedback in feedback_list:
            feedback_type = feedback.feedback_type.value
            type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
        return type_counts