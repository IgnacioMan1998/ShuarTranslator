"""Supabase implementation of Translation repository."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.features.translation.domain.entities.translation import Translation, Language, TranslationStatus, TranslationContext
from app.features.translation.domain.repositories.translation_repository import ITranslationRepository
from app.core.infrastructure.supabase_client import SupabaseClient
from app.core.shared.exceptions import NotFoundError
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseTranslationRepository(ITranslationRepository):
    """Supabase implementation of the Translation repository."""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.client = supabase_client
        self.table_name = "translations"
    
    async def save(self, translation: Translation) -> Translation:
        """Save a translation entity to Supabase."""
        try:
            translation_data = self._translation_to_dict(translation)
            
            result = await self.client.insert_record(
                self.table_name,
                translation_data,
                use_service_role=True
            )
            
            return self._dict_to_translation(result)
            
        except Exception as e:
            logger.error(f"Failed to save translation", error=str(e))
            raise
    
    async def find_by_id(self, translation_id: UUID) -> Optional[Translation]:
        """Find a translation by its unique identifier."""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(translation_id)).execute()
            
            if result.data:
                return self._dict_to_translation(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to find translation by ID: {translation_id}", error=str(e))
            raise
    
    async def find_by_source_text(
        self, 
        source_text: str, 
        source_language: Language
    ) -> List[Translation]:
        """Find translations by source text and language."""
        try:
            result = self.client.table(self.table_name).select("*").eq("source_text", source_text).eq("source_language", source_language.value).execute()
            
            return [self._dict_to_translation(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find translations by source text: {source_text}", error=str(e))
            raise
    
    async def find_by_target_text(
        self, 
        target_text: str, 
        target_language: Language
    ) -> List[Translation]:
        """Find translations by target text and language."""
        try:
            result = self.client.table(self.table_name).select("*").eq("target_text", target_text).eq("target_language", target_language.value).execute()
            
            return [self._dict_to_translation(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find translations by target text: {target_text}", error=str(e))
            raise
    
    async def find_by_status(self, status: TranslationStatus) -> List[Translation]:
        """Find translations by their approval status."""
        try:
            result = self.client.table(self.table_name).select("*").eq("status", status.value).execute()
            
            return [self._dict_to_translation(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find translations by status: {status}", error=str(e))
            raise
    
    async def find_pending_approval(self) -> List[Translation]:
        """Find translations pending expert approval."""
        try:
            result = self.client.table(self.table_name).select("*").eq("status", "pending").order("created_at").execute()
            
            return [self._dict_to_translation(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find pending translations", error=str(e))
            raise
    
    async def find_most_used(self, limit: int = 100) -> List[Translation]:
        """Find most frequently used translations."""
        try:
            result = self.client.table(self.table_name).select("*").order("usage_count", desc=True).limit(limit).execute()
            
            return [self._dict_to_translation(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find most used translations", error=str(e))
            raise
    
    async def update(self, translation: Translation) -> Translation:
        """Update an existing translation entity."""
        try:
            translation_data = self._translation_to_dict(translation)
            
            result = await self.client.update_record(
                self.table_name,
                translation_data,
                "id",
                str(translation.id),
                use_service_role=True
            )
            
            if result:
                return self._dict_to_translation(result)
            else:
                raise NotFoundError(f"Translation with ID {translation.id} not found for update")
                
        except Exception as e:
            logger.error(f"Failed to update translation: {translation.id}", error=str(e))
            raise
    
    async def delete(self, translation_id: UUID) -> bool:
        """Delete a translation by its ID."""
        try:
            success = await self.client.delete_record(
                self.table_name,
                "id",
                str(translation_id),
                use_service_role=True
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete translation: {translation_id}", error=str(e))
            raise
    
    async def exists(self, translation_id: UUID) -> bool:
        """Check if a translation exists by its ID."""
        try:
            result = self.client.table(self.table_name).select("id").eq("id", str(translation_id)).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check translation existence: {translation_id}", error=str(e))
            raise
    
    async def bulk_save(self, translations: List[Translation]) -> List[Translation]:
        """Save multiple translations in a single operation."""
        try:
            translations_data = [self._translation_to_dict(t) for t in translations]
            
            result = await self.client.insert_records(
                self.table_name,
                translations_data,
                use_service_role=True
            )
            
            return [self._dict_to_translation(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to bulk save {len(translations)} translations", error=str(e))
            raise
    
    async def count_total(self) -> int:
        """Get total count of translations."""
        try:
            result = self.client.table(self.table_name).select("id", count="exact").execute()
            return result.count
            
        except Exception as e:
            logger.error("Failed to count total translations", error=str(e))
            raise
    
    # Simplified implementations for other methods...
    async def find_bidirectional_pair(self, text1: str, text2: str) -> Optional[List[Translation]]:
        return []
    
    async def find_by_language_pair(self, source_language: Language, target_language: Language, limit: int = 100) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").eq("source_language", source_language.value).eq("target_language", target_language.value).limit(limit).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error(f"Failed to find translations by language pair", error=str(e))
            raise
    
    async def find_needs_review(self) -> List[Translation]:
        return await self.find_by_status(TranslationStatus.NEEDS_REVIEW)
    
    async def find_by_creator(self, creator_id: UUID) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").eq("created_by", str(creator_id)).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error(f"Failed to find translations by creator", error=str(e))
            raise
    
    async def find_by_approver(self, approver_id: UUID) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").eq("approved_by", str(approver_id)).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error(f"Failed to find translations by approver", error=str(e))
            raise
    
    async def find_high_rated(self, min_rating: float = 4.0, min_total_ratings: int = 3) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").gte("average_rating", min_rating).gte("total_ratings", min_total_ratings).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find high rated translations", error=str(e))
            raise
    
    async def find_low_rated(self, max_rating: float = 2.0, min_total_ratings: int = 3) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").lte("average_rating", max_rating).gte("total_ratings", min_total_ratings).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find low rated translations", error=str(e))
            raise
    
    async def find_recently_created(self, since: datetime, limit: int = 50) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").gte("created_at", since.isoformat()).order("created_at", desc=True).limit(limit).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find recently created translations", error=str(e))
            raise
    
    async def find_recently_updated(self, since: datetime, limit: int = 50) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").gte("updated_at", since.isoformat()).order("updated_at", desc=True).limit(limit).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find recently updated translations", error=str(e))
            raise
    
    async def find_by_confidence_range(self, min_confidence: float, max_confidence: float) -> List[Translation]:
        try:
            result = self.client.table(self.table_name).select("*").gte("confidence_score", min_confidence).lte("confidence_score", max_confidence).execute()
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error("Failed to find translations by confidence range", error=str(e))
            raise
    
    async def find_with_word_references(self, word_ids: List[UUID]) -> List[Translation]:
        # This would require array operations in PostgreSQL
        return []
    
    async def search_translations(self, query: str, language: Optional[Language] = None, limit: int = 50) -> List[Translation]:
        try:
            if language:
                if language == Language.SHUAR:
                    result = self.client.table(self.table_name).select("*").ilike("source_text", f"%{query}%").eq("source_language", "shuar").limit(limit).execute()
                else:
                    result = self.client.table(self.table_name).select("*").ilike("target_text", f"%{query}%").eq("target_language", "spanish").limit(limit).execute()
            else:
                result = self.client.table(self.table_name).select("*").ilike("source_text", f"%{query}%").limit(limit).execute()
            
            return [self._dict_to_translation(row) for row in result.data]
        except Exception as e:
            logger.error(f"Failed to search translations: {query}", error=str(e))
            raise
    
    async def get_translation_statistics(self) -> Dict[str, Any]:
        try:
            total = await self.count_total()
            approved = await self.count_by_status(TranslationStatus.APPROVED)
            pending = await self.count_by_status(TranslationStatus.PENDING)
            
            return {
                "total_translations": total,
                "approved_translations": approved,
                "pending_translations": pending,
                "approval_rate": approved / total if total > 0 else 0.0
            }
        except Exception as e:
            logger.error("Failed to get translation statistics", error=str(e))
            raise
    
    async def get_usage_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        # Would require more complex queries
        return {"message": "Analytics not implemented yet"}
    
    async def exists_exact_match(self, source_text: str, target_text: str, source_language: Language, target_language: Language) -> bool:
        try:
            result = self.client.table(self.table_name).select("id").eq("source_text", source_text).eq("target_text", target_text).eq("source_language", source_language.value).eq("target_language", target_language.value).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error("Failed to check exact match", error=str(e))
            raise
    
    async def bulk_update_status(self, translation_ids: List[UUID], status: TranslationStatus, updated_by: UUID) -> int:
        # Would require batch update operations
        return 0
    
    async def count_by_status(self, status: TranslationStatus) -> int:
        try:
            result = self.client.table(self.table_name).select("id", count="exact").eq("status", status.value).execute()
            return result.count
        except Exception as e:
            logger.error(f"Failed to count by status: {status}", error=str(e))
            raise
    
    async def count_by_language_pair(self, source_language: Language, target_language: Language) -> int:
        try:
            result = self.client.table(self.table_name).select("id", count="exact").eq("source_language", source_language.value).eq("target_language", target_language.value).execute()
            return result.count
        except Exception as e:
            logger.error("Failed to count by language pair", error=str(e))
            raise
    
    async def get_average_rating(self) -> float:
        # Would require aggregate functions
        return 0.0
    
    async def get_average_confidence(self) -> float:
        # Would require aggregate functions
        return 0.0
    
    def _translation_to_dict(self, translation: Translation) -> Dict[str, Any]:
        """Convert Translation entity to dictionary for database storage."""
        data = {
            "id": str(translation.id),
            "source_text": translation.source_text,
            "target_text": translation.target_text,
            "source_language": translation.source_language.value,
            "target_language": translation.target_language.value,
            "confidence_score": translation.confidence_score,
            "average_rating": translation.average_rating,
            "total_ratings": translation.total_ratings,
            "usage_count": translation.usage_count,
            "status": translation.status.value,
            "created_at": translation.created_at.isoformat(),
            "updated_at": translation.updated_at.isoformat()
        }
        
        if translation.created_by:
            data["created_by"] = str(translation.created_by)
        
        if translation.approved_by:
            data["approved_by"] = str(translation.approved_by)
        
        if translation.approved_at:
            data["approved_at"] = translation.approved_at.isoformat()
        
        if translation.context:
            data.update({
                "context_domain": translation.context.domain,
                "context_register": translation.context.register,
                "context_dialect": translation.context.dialect,
                "cultural_notes": translation.context.cultural_notes
            })
        
        return data
    
    def _dict_to_translation(self, data: Dict[str, Any]) -> Translation:
        """Convert database dictionary to Translation entity."""
        context = None
        if any(data.get(key) for key in ["context_domain", "context_register", "context_dialect", "cultural_notes"]):
            context = TranslationContext(
                domain=data.get("context_domain"),
                register=data.get("context_register"),
                dialect=data.get("context_dialect"),
                cultural_notes=data.get("cultural_notes")
            )
        
        return Translation(
            id=UUID(data["id"]),
            source_text=data["source_text"],
            target_text=data["target_text"],
            source_language=Language(data["source_language"]),
            target_language=Language(data["target_language"]),
            confidence_score=data.get("confidence_score", 0.5),
            context=context,
            usage_count=data.get("usage_count", 0),
            average_rating=data.get("average_rating", 0.0),
            total_ratings=data.get("total_ratings", 0),
            status=TranslationStatus(data.get("status", "pending")),
            created_by=UUID(data["created_by"]) if data.get("created_by") else None,
            approved_by=UUID(data["approved_by"]) if data.get("approved_by") else None,
            created_at=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00')),
            approved_at=datetime.fromisoformat(data["approved_at"].replace('Z', '+00:00')) if data.get("approved_at") else None
        )