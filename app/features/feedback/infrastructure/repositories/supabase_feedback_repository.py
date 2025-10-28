"""Supabase implementation of Feedback repository."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.features.feedback.domain.entities.feedback import Feedback, FeedbackType, FeedbackStatus, UserRole
from app.features.feedback.domain.repositories.feedback_repository import IFeedbackRepository
from app.core.infrastructure.supabase_client import SupabaseClient
from app.core.shared.exceptions import NotFoundError
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseFeedbackRepository(IFeedbackRepository):
    """Supabase implementation of the Feedback repository."""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.client = supabase_client
        self.table_name = "translation_feedback"
    
    async def save(self, feedback: Feedback) -> Feedback:
        """Save a feedback entity to Supabase."""
        try:
            feedback_data = self._feedback_to_dict(feedback)
            
            result = await self.client.insert_record(
                self.table_name,
                feedback_data,
                use_service_role=True
            )
            
            return self._dict_to_feedback(result)
            
        except Exception as e:
            logger.error(f"Failed to save feedback", error=str(e))
            raise
    
    async def find_by_id(self, feedback_id: UUID) -> Optional[Feedback]:
        """Find feedback by its unique identifier."""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(feedback_id)).execute()
            
            if result.data:
                return self._dict_to_feedback(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to find feedback by ID: {feedback_id}", error=str(e))
            raise
    
    async def find_by_translation_id(self, translation_id: UUID) -> List[Feedback]:
        """Find all feedback for a specific translation."""
        try:
            result = self.client.table(self.table_name).select("*").eq("translation_id", str(translation_id)).order("created_at", desc=True).execute()
            
            return [self._dict_to_feedback(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find feedback by translation ID: {translation_id}", error=str(e))
            raise
    
    async def find_by_user_id(self, user_id: UUID) -> List[Feedback]:
        """Find all feedback submitted by a specific user."""
        try:
            result = self.client.table(self.table_name).select("*").eq("user_id", str(user_id)).order("created_at", desc=True).execute()
            
            return [self._dict_to_feedback(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find feedback by user ID: {user_id}", error=str(e))
            raise
    
    async def find_by_status(self, status: FeedbackStatus) -> List[Feedback]:
        """Find feedback by approval status."""
        try:
            result = self.client.table(self.table_name).select("*").eq("status", status.value).order("created_at", desc=True).execute()
            
            return [self._dict_to_feedback(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find feedback by status: {status}", error=str(e))
            raise
    
    async def find_pending_review(self) -> List[Feedback]:
        """Find feedback pending expert review."""
        try:
            result = self.client.table(self.table_name).select("*").eq("status", "pending").order("created_at").execute()
            
            return [self._dict_to_feedback(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find pending feedback", error=str(e))
            raise
    
    async def find_from_native_speakers(self) -> List[Feedback]:
        """Find feedback from verified native Shuar speakers."""
        try:
            result = self.client.table(self.table_name).select("*").eq("is_from_native_speaker", True).order("created_at", desc=True).execute()
            
            return [self._dict_to_feedback(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find native speaker feedback", error=str(e))
            raise
    
    async def update(self, feedback: Feedback) -> Feedback:
        """Update an existing feedback entity."""
        try:
            feedback_data = self._feedback_to_dict(feedback)
            
            result = await self.client.update_record(
                self.table_name,
                feedback_data,
                "id",
                str(feedback.id),
                use_service_role=True
            )
            
            if result:
                return self._dict_to_feedback(result)
            else:
                raise NotFoundError(f"Feedback with ID {feedback.id} not found for update")
                
        except Exception as e:
            logger.error(f"Failed to update feedback: {feedback.id}", error=str(e))
            raise
    
    async def delete(self, feedback_id: UUID) -> bool:
        """Delete feedback by its ID."""
        try:
            success = await self.client.delete_record(
                self.table_name,
                "id",
                str(feedback_id),
                use_service_role=True
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete feedback: {feedback_id}", error=str(e))
            raise
    
    async def exists(self, feedback_id: UUID) -> bool:
        """Check if feedback exists by its ID."""
        try:
            result = self.client.table(self.table_name).select("id").eq("id", str(feedback_id)).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check feedback existence: {feedback_id}", error=str(e))
            raise
    
    async def has_user_rated_translation(self, user_id: UUID, translation_id: UUID) -> bool:
        """Check if a user has already rated a specific translation."""
        try:
            result = self.client.table(self.table_name).select("id").eq("user_id", str(user_id)).eq("translation_id", str(translation_id)).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check user rating existence", error=str(e))
            raise
    
    async def count_total(self) -> int:
        """Get total count of feedback entries."""
        try:
            result = self.client.table(self.table_name).select("id", count="exact").execute()
            return result.count
            
        except Exception as e:
            logger.error("Failed to count total feedback", error=str(e))
            raise
    
    # Simplified implementations for other methods...
    async def find_by_feedback_type(self, feedback_type: FeedbackType) -> List[Feedback]:
        try:
            result = self.client.table(self.table_name).select("*").eq("feedback_type", feedback_type.value).execute()
            return [self._dict_to_feedback(row) for row in result.data]
        except Exception as e:
            logger.error(f"Failed to find feedback by type: {feedback_type}", error=str(e))
            raise
    
    async def find_by_user_role(self, user_role: UserRole) -> List[Feedback]:
        try:
            result = self.client.table(self.table_name).select("*").eq("user_role", user_role.value).execute()
            return [self._dict_to_feedback(row) for row in result.data]
        except Exception as e:
            logger.error(f"Failed to find feedback by user role: {user_role}", error=str(e))
            raise
    
    async def find_high_value_feedback(self) -> List[Feedback]:
        # Would need complex filtering logic
        return await self.find_from_native_speakers()
    
    async def find_needs_expert_attention(self) -> List[Feedback]:
        # Would need complex filtering logic
        return await self.find_pending_review()
    
    async def find_by_rating_range(self, min_rating: int, max_rating: int) -> List[Feedback]:
        try:
            result = self.client.table(self.table_name).select("*").gte("rating", min_rating).lte("rating", max_rating).execute()
            return [self._dict_to_feedback(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find feedback by rating range", error=str(e))
            raise
    
    async def find_with_suggestions(self) -> List[Feedback]:
        try:
            result = self.client.table(self.table_name).select("*").not_.is_("suggested_translation", "null").execute()
            return [self._dict_to_feedback(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find feedback with suggestions", error=str(e))
            raise
    
    async def find_with_cultural_notes(self) -> List[Feedback]:
        try:
            result = self.client.table(self.table_name).select("*").not_.is_("cultural_context", "null").execute()
            return [self._dict_to_feedback(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find feedback with cultural notes", error=str(e))
            raise
    
    async def find_recently_submitted(self, since: datetime, limit: int = 50) -> List[Feedback]:
        try:
            result = self.client.table(self.table_name).select("*").gte("created_at", since.isoformat()).order("created_at", desc=True).limit(limit).execute()
            return [self._dict_to_feedback(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find recent feedback", error=str(e))
            raise
    
    async def find_reviewed_by_expert(self, expert_id: UUID) -> List[Feedback]:
        try:
            result = self.client.table(self.table_name).select("*").eq("reviewed_by", str(expert_id)).execute()
            return [self._dict_to_feedback(row) for row in result.data]
        except Exception as e:
            logger.error(f"Failed to find feedback reviewed by expert: {expert_id}", error=str(e))
            raise
    
    async def find_approved_feedback(self) -> List[Feedback]:
        return await self.find_by_status(FeedbackStatus.APPROVED)
    
    async def find_rejected_feedback(self) -> List[Feedback]:
        return await self.find_by_status(FeedbackStatus.REJECTED)
    
    async def find_implemented_feedback(self) -> List[Feedback]:
        return await self.find_by_status(FeedbackStatus.IMPLEMENTED)
    
    async def get_feedback_statistics(self) -> Dict[str, Any]:
        try:
            total = await self.count_total()
            pending = await self.count_by_status(FeedbackStatus.PENDING)
            approved = await self.count_by_status(FeedbackStatus.APPROVED)
            
            return {
                "total_feedback": total,
                "pending_feedback": pending,
                "approved_feedback": approved,
                "approval_rate": approved / total if total > 0 else 0.0
            }
        except Exception as e:
            logger.error("Failed to get feedback statistics", error=str(e))
            raise
    
    async def get_translation_feedback_summary(self, translation_id: UUID) -> Dict[str, Any]:
        feedback_list = await self.find_by_translation_id(translation_id)
        
        if not feedback_list:
            return {"total_feedback": 0, "average_rating": 0.0}
        
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        return {
            "total_feedback": len(feedback_list),
            "average_rating": avg_rating,
            "native_speaker_count": sum(1 for f in feedback_list if f.is_from_native_speaker)
        }
    
    async def get_user_feedback_statistics(self, user_id: UUID) -> Dict[str, Any]:
        feedback_list = await self.find_by_user_id(user_id)
        
        return {
            "total_feedback_given": len(feedback_list),
            "average_rating_given": sum(f.rating for f in feedback_list if f.rating) / len([f for f in feedback_list if f.rating]) if feedback_list else 0.0
        }
    
    async def calculate_weighted_average_rating(self, translation_id: UUID) -> Optional[float]:
        feedback_list = await self.find_by_translation_id(translation_id)
        
        if not feedback_list:
            return None
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for feedback in feedback_list:
            if feedback.rating:
                weight = feedback.get_weight()
                weighted_sum += feedback.rating * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else None
    
    async def get_feedback_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        # Would require more complex time-series queries
        return {"message": "Trends not implemented yet"}
    
    async def bulk_save(self, feedback_list: List[Feedback]) -> List[Feedback]:
        try:
            feedback_data = [self._feedback_to_dict(f) for f in feedback_list]
            
            result = await self.client.insert_records(
                self.table_name,
                feedback_data,
                use_service_role=True
            )
            
            return [self._dict_to_feedback(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to bulk save {len(feedback_list)} feedback items", error=str(e))
            raise
    
    async def bulk_update_status(self, feedback_ids: List[UUID], status: FeedbackStatus, reviewed_by: UUID, expert_notes: Optional[str] = None) -> int:
        # Would require batch update operations
        return 0
    
    async def count_by_status(self, status: FeedbackStatus) -> int:
        try:
            result = self.client.table(self.table_name).select("id", count="exact").eq("status", status.value).execute()
            return result.count
        except Exception as e:
            logger.error(f"Failed to count by status: {status}", error=str(e))
            raise
    
    async def count_by_type(self, feedback_type: FeedbackType) -> int:
        try:
            result = self.client.table(self.table_name).select("id", count="exact").eq("feedback_type", feedback_type.value).execute()
            return result.count
        except Exception as e:
            logger.error(f"Failed to count by type: {feedback_type}", error=str(e))
            raise
    
    async def count_by_user_role(self, user_role: UserRole) -> int:
        try:
            result = self.client.table(self.table_name).select("id", count="exact").eq("user_role", user_role.value).execute()
            return result.count
        except Exception as e:
            logger.error(f"Failed to count by user role: {user_role}", error=str(e))
            raise
    
    async def count_from_native_speakers(self) -> int:
        try:
            result = self.client.table(self.table_name).select("id", count="exact").eq("is_from_native_speaker", True).execute()
            return result.count
        except Exception as e:
            logger.error("Failed to count native speaker feedback", error=str(e))
            raise
    
    async def get_average_rating_by_translation(self, translation_id: UUID) -> Optional[float]:
        feedback_list = await self.find_by_translation_id(translation_id)
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        return sum(ratings) / len(ratings) if ratings else None
    
    async def get_rating_distribution(self, translation_id: UUID) -> Dict[int, int]:
        feedback_list = await self.find_by_translation_id(translation_id)
        distribution = {}
        
        for feedback in feedback_list:
            if feedback.rating:
                distribution[feedback.rating] = distribution.get(feedback.rating, 0) + 1
        
        return distribution
    
    def _feedback_to_dict(self, feedback: Feedback) -> Dict[str, Any]:
        """Convert Feedback entity to dictionary for database storage."""
        data = {
            "id": str(feedback.id),
            "translation_id": str(feedback.translation_id),
            "user_role": feedback.user_role.value,
            "feedback_type": feedback.feedback_type.value,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "suggested_translation": feedback.suggested_translation,
            "cultural_context": feedback.cultural_context,
            "pronunciation_notes": feedback.pronunciation_notes,
            "is_from_native_speaker": feedback.is_from_native_speaker,
            "status": feedback.status.value,
            "expert_notes": feedback.expert_notes,
            "created_at": feedback.created_at.isoformat(),
            "updated_at": feedback.updated_at.isoformat()
        }
        
        if feedback.user_id:
            data["user_id"] = str(feedback.user_id)
        
        if feedback.reviewed_by:
            data["reviewed_by"] = str(feedback.reviewed_by)
        
        if feedback.reviewed_at:
            data["reviewed_at"] = feedback.reviewed_at.isoformat()
        
        return data
    
    def _dict_to_feedback(self, data: Dict[str, Any]) -> Feedback:
        """Convert database dictionary to Feedback entity."""
        return Feedback(
            id=UUID(data["id"]),
            translation_id=UUID(data["translation_id"]),
            user_id=UUID(data["user_id"]) if data.get("user_id") else None,
            user_role=UserRole(data["user_role"]),
            feedback_type=FeedbackType(data["feedback_type"]),
            rating=data.get("rating"),
            comment=data.get("comment"),
            suggested_translation=data.get("suggested_translation"),
            cultural_context=data.get("cultural_context"),
            pronunciation_notes=data.get("pronunciation_notes"),
            is_from_native_speaker=data.get("is_from_native_speaker", False),
            status=FeedbackStatus(data.get("status", "pending")),
            expert_notes=data.get("expert_notes"),
            reviewed_by=UUID(data["reviewed_by"]) if data.get("reviewed_by") else None,
            reviewed_at=datetime.fromisoformat(data["reviewed_at"].replace('Z', '+00:00')) if data.get("reviewed_at") else None,
            created_at=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        )