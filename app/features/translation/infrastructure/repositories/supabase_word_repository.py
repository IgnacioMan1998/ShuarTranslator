"""Supabase implementation of Word repository."""

from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from app.features.translation.domain.entities.word import Word, WordType, VocalType, PhonologicalInfo, MorphologicalInfo
from app.features.translation.domain.repositories.word_repository import IWordRepository
from app.core.infrastructure.supabase_client import SupabaseClient
from app.core.shared.exceptions import NotFoundError, ValidationError
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseWordRepository(IWordRepository):
    """Supabase implementation of the Word repository."""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.client = supabase_client
        self.table_name = "palabras_detalladas"
    
    async def save(self, word: Word) -> Word:
        """Save a word entity to Supabase."""
        try:
            word_data = self._word_to_dict(word)
            
            result = await self.client.insert_record(
                self.table_name,
                word_data,
                use_service_role=True
            )
            
            return self._dict_to_word(result)
            
        except Exception as e:
            logger.error(f"Failed to save word: {word.shuar_text}", error=str(e))
            raise
    
    async def find_by_id(self, word_id: UUID) -> Optional[Word]:
        """Find a word by its unique identifier."""
        try:
            result = self.client.table(self.table_name).select("*").eq("id", str(word_id)).execute()
            
            if result.data:
                return self._dict_to_word(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to find word by ID: {word_id}", error=str(e))
            raise
    
    async def find_by_shuar_text(self, shuar_text: str) -> Optional[Word]:
        """Find a word by its Shuar text (exact match)."""
        try:
            result = self.client.table(self.table_name).select("*").eq("palabra_shuar", shuar_text.lower()).execute()
            
            if result.data:
                return self._dict_to_word(result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to find word by Shuar text: {shuar_text}", error=str(e))
            raise
    
    async def find_by_spanish_translation(self, spanish_text: str) -> List[Word]:
        """Find words by Spanish translation (can have multiple matches)."""
        try:
            result = self.client.table(self.table_name).select("*").ilike("palabra_espanol", f"%{spanish_text}%").execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find words by Spanish text: {spanish_text}", error=str(e))
            raise
    
    async def search_similar_shuar_words(
        self, 
        shuar_text: str, 
        similarity_threshold: float = 0.5,
        limit: int = 10
    ) -> List[Word]:
        """Find Shuar words similar to the given text based on phonological similarity."""
        try:
            # Use PostgreSQL similarity functions if available
            # For now, use LIKE pattern matching as a fallback
            pattern = f"%{shuar_text}%"
            
            result = self.client.table(self.table_name).select("*").ilike("palabra_shuar", pattern).limit(limit).execute()
            
            words = [self._dict_to_word(row) for row in result.data]
            
            # Filter out exact matches
            words = [w for w in words if w.shuar_text.lower() != shuar_text.lower()]
            
            return words[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search similar Shuar words: {shuar_text}", error=str(e))
            raise
    
    async def search_similar_spanish_words(
        self, 
        spanish_text: str, 
        similarity_threshold: float = 0.5,
        limit: int = 10
    ) -> List[Word]:
        """Find words with similar Spanish translations."""
        try:
            pattern = f"%{spanish_text}%"
            
            result = self.client.table(self.table_name).select("*").ilike("palabra_espanol", pattern).limit(limit).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to search similar Spanish words: {spanish_text}", error=str(e))
            raise
    
    async def find_by_root_word(self, root_word: str) -> List[Word]:
        """Find words that share the same morphological root."""
        try:
            result = self.client.table(self.table_name).select("*").eq("raiz_palabra", root_word).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find words by root: {root_word}", error=str(e))
            raise
    
    async def find_by_vocal_types(self, vocal_types: List[VocalType]) -> List[Word]:
        """Find words containing specific vocal types."""
        try:
            # This would require custom SQL or RPC function for complex filtering
            # For now, get all words and filter in memory (not efficient for large datasets)
            result = self.client.table(self.table_name).select("*").execute()
            
            words = [self._dict_to_word(row) for row in result.data]
            
            # Filter by vocal types
            filtered_words = []
            for word in words:
                if word.phonological_info and word.phonological_info.vocal_types_present:
                    word_types = set(word.phonological_info.vocal_types_present)
                    required_types = set(vocal_types)
                    if word_types & required_types:  # Intersection
                        filtered_words.append(word)
            
            return filtered_words
            
        except Exception as e:
            logger.error(f"Failed to find words by vocal types", error=str(e))
            raise
    
    async def find_by_word_type(self, word_type: WordType) -> List[Word]:
        """Find words of a specific grammatical type."""
        try:
            # Map WordType enum to database values
            type_mapping = {
                WordType.NOUN: "sustantivo",
                WordType.VERB: "verbo",
                WordType.ADJECTIVE: "adjetivo",
                WordType.ADVERB: "adverbio",
                WordType.PRONOUN: "pronombre",
                WordType.CONJUNCTION: "conjuncion",
                WordType.PREPOSITION: "preposicion",
                WordType.INTERJECTION: "interjeccion"
            }
            
            db_type = type_mapping.get(word_type, word_type.value)
            
            result = self.client.table(self.table_name).select("*").eq("tipo_palabra_id", db_type).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find words by type: {word_type}", error=str(e))
            raise
    
    async def find_compound_words(self) -> List[Word]:
        """Find all compound words in the repository."""
        try:
            result = self.client.table(self.table_name).select("*").eq("es_compuesta", True).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find compound words", error=str(e))
            raise
    
    async def find_words_with_suffix(self, suffix: str) -> List[Word]:
        """Find words that contain a specific suffix."""
        try:
            # Use array contains operator for suffixes
            result = self.client.table(self.table_name).select("*").contains("sufijos_aplicados", [suffix]).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find words with suffix: {suffix}", error=str(e))
            raise
    
    async def find_most_frequent(self, limit: int = 100) -> List[Word]:
        """Find the most frequently used words."""
        try:
            result = self.client.table(self.table_name).select("*").order("frecuencia_uso", desc=True).limit(limit).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find most frequent words", error=str(e))
            raise
    
    async def find_recently_added(self, limit: int = 50) -> List[Word]:
        """Find recently added words."""
        try:
            result = self.client.table(self.table_name).select("*").order("fecha_creacion", desc=True).limit(limit).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find recently added words", error=str(e))
            raise
    
    async def find_unverified_words(self) -> List[Word]:
        """Find words that haven't been verified by experts."""
        try:
            result = self.client.table(self.table_name).select("*").eq("is_verified", False).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error("Failed to find unverified words", error=str(e))
            raise
    
    async def find_low_confidence_words(self, threshold: float = 0.5) -> List[Word]:
        """Find words with confidence below threshold."""
        try:
            result = self.client.table(self.table_name).select("*").lt("nivel_confianza", threshold).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to find low confidence words below {threshold}", error=str(e))
            raise
    
    async def search_full_text(
        self, 
        query: str, 
        language: str = "both",
        limit: int = 50
    ) -> List[Word]:
        """Perform full-text search across Shuar text, Spanish translation, and definitions."""
        try:
            # Use PostgreSQL full-text search if available
            # For now, use simple ILIKE search
            conditions = []
            
            if language in ["shuar", "both"]:
                conditions.append(f"palabra_shuar ILIKE '%{query}%'")
            
            if language in ["spanish", "both"]:
                conditions.append(f"palabra_espanol ILIKE '%{query}%'")
                conditions.append(f"definicion_extendida ILIKE '%{query}%'")
            
            # This would require custom RPC function for complex OR conditions
            # For now, search in Spanish fields
            result = self.client.table(self.table_name).select("*").ilike("palabra_espanol", f"%{query}%").limit(limit).execute()
            
            return [self._dict_to_word(row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Failed to perform full-text search: {query}", error=str(e))
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics (total words, by type, etc.)."""
        try:
            # Get total count
            total_result = self.client.table(self.table_name).select("id", count="exact").execute()
            total_count = total_result.count
            
            # Get verified count
            verified_result = self.client.table(self.table_name).select("id", count="exact").eq("is_verified", True).execute()
            verified_count = verified_result.count
            
            return {
                "total_words": total_count,
                "verified_words": verified_count,
                "unverified_words": total_count - verified_count,
                "verification_rate": verified_count / total_count if total_count > 0 else 0.0
            }
            
        except Exception as e:
            logger.error("Failed to get word statistics", error=str(e))
            raise
    
    async def update(self, word: Word) -> Word:
        """Update an existing word entity."""
        try:
            word_data = self._word_to_dict(word)
            
            result = await self.client.update_record(
                self.table_name,
                word_data,
                "id",
                str(word.id),
                use_service_role=True
            )
            
            if result:
                return self._dict_to_word(result)
            else:
                raise NotFoundError(f"Word with ID {word.id} not found for update")
                
        except Exception as e:
            logger.error(f"Failed to update word: {word.id}", error=str(e))
            raise
    
    async def delete(self, word_id: UUID) -> bool:
        """Delete a word by its ID."""
        try:
            success = await self.client.delete_record(
                self.table_name,
                "id",
                str(word_id),
                use_service_role=True
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete word: {word_id}", error=str(e))
            raise
    
    async def exists(self, word_id: UUID) -> bool:
        """Check if a word exists by its ID."""
        try:
            result = self.client.table(self.table_name).select("id").eq("id", str(word_id)).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check word existence: {word_id}", error=str(e))
            raise
    
    async def exists_by_shuar_text(self, shuar_text: str) -> bool:
        """Check if a word exists by its Shuar text."""
        try:
            result = self.client.table(self.table_name).select("id").eq("palabra_shuar", shuar_text.lower()).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check word existence by text: {shuar_text}", error=str(e))
            raise
    
    async def bulk_save(self, words: List[Word]) -> List[Word]:
        """Save multiple words in a single operation."""
        try:
            words_data = [self._word_to_dict(word) for word in words]
            
            result = await self.client.insert_records(
                self.table_name,
                words_data,
                use_service_role=True
            )
            
            return [self._dict_to_word(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to bulk save {len(words)} words", error=str(e))
            raise
    
    async def count_total(self) -> int:
        """Get total count of words in repository."""
        try:
            result = self.client.table(self.table_name).select("id", count="exact").execute()
            return result.count
            
        except Exception as e:
            logger.error("Failed to count total words", error=str(e))
            raise
    
    async def count_by_word_type(self, word_type: WordType) -> int:
        """Get count of words by grammatical type."""
        try:
            # This would need proper mapping to database word type IDs
            result = self.client.table(self.table_name).select("id", count="exact").eq("tipo_palabra", word_type.value).execute()
            return result.count
            
        except Exception as e:
            logger.error(f"Failed to count words by type: {word_type}", error=str(e))
            raise
    
    async def count_verified(self) -> int:
        """Get count of verified words."""
        try:
            result = self.client.table(self.table_name).select("id", count="exact").eq("is_verified", True).execute()
            return result.count
            
        except Exception as e:
            logger.error("Failed to count verified words", error=str(e))
            raise
    
    def _word_to_dict(self, word: Word) -> Dict[str, Any]:
        """Convert Word entity to dictionary for database storage."""
        data = {
            "id": str(word.id),
            "palabra_shuar": word.shuar_text,
            "palabra_espanol": word.spanish_translation,
            "definicion_extendida": word.definition_extended,
            "frecuencia_uso": word.frequency_score,
            "nivel_confianza": word.confidence_level,
            "is_verified": word.is_verified,
            "sinonimos": word.synonyms,
            "antonimos": word.antonyms,
            "notas_culturales": word.cultural_notes,
            "ejemplos_uso": json.dumps(word.usage_examples) if word.usage_examples else None,
            "variantes_dialectales": json.dumps(word.dialect_variations) if word.dialect_variations else None,
            "fecha_creacion": word.created_at.isoformat(),
            "fecha_ultima_modificacion": word.updated_at.isoformat()
        }
        
        # Add word type if available
        if word.word_type:
            data["tipo_palabra"] = word.word_type.value
        
        # Add phonological info if available
        if word.phonological_info:
            data.update({
                "transcripcion_ipa": word.phonological_info.ipa_transcription,
                "tiene_nasalizacion": word.phonological_info.has_nasal_vowels,
                "tiene_laringalizacion": word.phonological_info.has_laryngealized_vowels,
                "numero_silabas": word.phonological_info.number_of_syllables,
                "patron_silabico": word.phonological_info.syllable_pattern
            })
        
        # Add morphological info if available
        if word.morphological_info:
            data.update({
                "raiz_palabra": word.morphological_info.root_word,
                "es_compuesta": word.morphological_info.is_compound,
                "componentes": json.dumps(word.morphological_info.compound_components),
                "sufijos_aplicados": word.morphological_info.applied_suffixes
            })
        
        return data
    
    def _dict_to_word(self, data: Dict[str, Any]) -> Word:
        """Convert database dictionary to Word entity."""
        # Parse phonological info
        phonological_info = None
        if data.get("transcripcion_ipa"):
            phonological_info = PhonologicalInfo(
                ipa_transcription=data["transcripcion_ipa"],
                has_nasal_vowels=data.get("tiene_nasalizacion", False),
                has_laryngealized_vowels=data.get("tiene_laringalizacion", False),
                vocal_types_present=[],  # Would need to be parsed from database
                number_of_syllables=data.get("numero_silabas", 0),
                syllable_pattern=data.get("patron_silabico")
            )
        
        # Parse morphological info
        morphological_info = None
        if data.get("raiz_palabra"):
            morphological_info = MorphologicalInfo(
                root_word=data["raiz_palabra"],
                is_compound=data.get("es_compuesta", False),
                compound_components=json.loads(data.get("componentes", "[]")) if data.get("componentes") else [],
                applied_suffixes=data.get("sufijos_aplicados", [])
            )
        
        # Parse word type
        word_type = None
        if data.get("tipo_palabra"):
            try:
                word_type = WordType(data["tipo_palabra"])
            except ValueError:
                pass  # Invalid word type, keep as None
        
        return Word(
            id=UUID(data["id"]),
            shuar_text=data["palabra_shuar"],
            spanish_translation=data["palabra_espanol"],
            word_type=word_type,
            phonological_info=phonological_info,
            morphological_info=morphological_info,
            definition_extended=data.get("definicion_extendida"),
            usage_examples=json.loads(data.get("ejemplos_uso", "[]")) if data.get("ejemplos_uso") else [],
            synonyms=data.get("sinonimos", []),
            antonyms=data.get("antonimos", []),
            cultural_notes=data.get("notas_culturales"),
            dialect_variations=json.loads(data.get("variantes_dialectales", "[]")) if data.get("variantes_dialectales") else [],
            frequency_score=data.get("frecuencia_uso", 0),
            confidence_level=data.get("nivel_confianza", 0.5),
            is_verified=data.get("is_verified", False)
        )