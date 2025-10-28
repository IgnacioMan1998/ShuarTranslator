"""Use case for translating text between Shuar and Spanish."""

from typing import Optional
from dataclasses import dataclass
import time

from app.features.translation.domain.entities.translation import Language
from app.features.translation.domain.value_objects.translation_result import TranslationResult, SimilarWord
from app.features.translation.domain.services.language_detection_service import LanguageDetectionService
from app.features.translation.domain.services.phonological_analysis_service import PhonologicalAnalysisService
from app.features.translation.domain.services.similarity_search_service import SimilaritySearchService, SearchCriteria
from app.core.shared.repositories import IWordRepository, ITranslationRepository
from app.core.shared.exceptions import ValidationError, NotFoundError
from app.core.utils.validators import ShuarTextValidator, SpanishTextValidator


@dataclass
class TranslateTextRequest:
    """Request for text translation."""
    text: str
    source_language: Optional[str] = None  # "shuar", "spanish", or None for auto-detection
    target_language: str = "auto"  # "shuar", "spanish", or "auto"
    include_phonetics: bool = True
    include_morphology: bool = True
    include_similar_words: bool = True
    max_similar_words: int = 5


class TranslateTextUseCase:
    """Use case for translating text between Shuar and Spanish."""
    
    def __init__(
        self,
        word_repository: IWordRepository,
        translation_repository: ITranslationRepository,
        language_detection_service: LanguageDetectionService,
        phonological_service: PhonologicalAnalysisService,
        similarity_service: SimilaritySearchService
    ):
        self.word_repository = word_repository
        self.translation_repository = translation_repository
        self.language_detection_service = language_detection_service
        self.phonological_service = phonological_service
        self.similarity_service = similarity_service
    
    async def execute(self, request: TranslateTextRequest) -> TranslationResult:
        """Execute the translation use case."""
        start_time = time.time()
        
        # Validate input
        self._validate_request(request)
        
        # Detect source language if not provided
        if not request.source_language or request.source_language == "auto":
            detection_result = self.language_detection_service.detect_language(request.text)
            detected_language = detection_result.detected_language
        else:
            detected_language = Language(request.source_language.lower())
        
        # Determine target language
        target_language = self._determine_target_language(
            detected_language, request.target_language
        )
        
        # Normalize text
        normalized_text = self._normalize_text(request.text, detected_language)
        
        # Try exact translation first
        exact_translations = await self._find_exact_translations(
            normalized_text, detected_language, target_language
        )
        
        if exact_translations:
            # Found exact translations
            translation_data = []
            max_confidence = 0.0
            
            for translation in exact_translations:
                confidence = translation.confidence_score
                max_confidence = max(max_confidence, confidence)
                
                translation_data.append({
                    "text": translation.target_text,
                    "confidence": confidence,
                    "type": "exact",
                    "source": "database",
                    "usage_count": translation.usage_count,
                    "average_rating": translation.average_rating
                })
                
                # Update usage count
                translation.increment_usage()
                await self.translation_repository.update(translation)
            
            # Get phonetic and morphological info if requested
            phonetic_info = None
            morphological_info = None
            
            if detected_language == Language.SHUAR:
                if request.include_phonetics:
                    phonetic_info = self._get_phonetic_info(normalized_text)
                if request.include_morphology:
                    morphological_info = await self._get_morphological_info(normalized_text)
            
            # Get similar words if requested and confidence is not very high
            similar_words = []
            if request.include_similar_words and max_confidence < 0.9:
                similar_words = await self._find_similar_words(
                    normalized_text, detected_language, request.max_similar_words
                )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return TranslationResult.create_successful(
                original_text=request.text,
                detected_language=detected_language.value,
                translations=translation_data,
                confidence_score=max_confidence,
                processing_time_ms=processing_time,
                phonetic_info=phonetic_info,
                morphological_analysis=morphological_info,
                similar_words=similar_words
            )
        
        else:
            # No exact translation found, provide similar words
            similar_words = await self._find_similar_words(
                normalized_text, detected_language, request.max_similar_words
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return TranslationResult.create_with_suggestions(
                original_text=request.text,
                detected_language=detected_language.value,
                similar_words=similar_words,
                processing_time_ms=processing_time
            )
    
    def _validate_request(self, request: TranslateTextRequest) -> None:
        """Validate the translation request."""
        if not request.text or not request.text.strip():
            raise ValidationError("Text cannot be empty")
        
        if len(request.text) > 500:
            raise ValidationError("Text exceeds maximum length of 500 characters")
        
        valid_languages = {"shuar", "spanish", "auto", None}
        if request.source_language and request.source_language.lower() not in valid_languages:
            raise ValidationError("Invalid source language")
        
        if request.target_language.lower() not in valid_languages:
            raise ValidationError("Invalid target language")
    
    def _determine_target_language(
        self, 
        source_language: Language, 
        target_language_str: str
    ) -> Language:
        """Determine the target language for translation."""
        if target_language_str == "auto":
            # Auto-determine opposite language
            return Language.SPANISH if source_language == Language.SHUAR else Language.SHUAR
        else:
            return Language(target_language_str.lower())
    
    def _normalize_text(self, text: str, language: Language) -> str:
        """Normalize text based on language."""
        if language == Language.SHUAR:
            return ShuarTextValidator.validate_shuar_text(text)
        else:
            return SpanishTextValidator.validate_spanish_text(text)
    
    async def _find_exact_translations(
        self, 
        text: str, 
        source_language: Language, 
        target_language: Language
    ) -> list:
        """Find exact translations in the database."""
        translations = await self.translation_repository.find_by_source_text(
            text, source_language
        )
        
        # Filter by target language and approved status
        exact_translations = [
            t for t in translations 
            if t.target_language == target_language and 
            t.status.value in ["approved", "pending"]  # Include pending for more results
        ]
        
        # Sort by confidence and rating
        exact_translations.sort(
            key=lambda t: (t.confidence_score, t.average_rating), 
            reverse=True
        )
        
        return exact_translations
    
    def _get_phonetic_info(self, shuar_text: str) -> dict:
        """Get phonetic information for Shuar text."""
        try:
            features = self.phonological_service.analyze_word(shuar_text)
            ipa_transcription = self.phonological_service.generate_ipa_transcription(shuar_text)
            
            return {
                "ipa_transcription": ipa_transcription,
                "vocal_types": [vt.value for vt in features.vocal_types],
                "has_digraphs": features.has_digraphs,
                "digraphs_present": features.digraphs_present,
                "syllable_count": features.syllable_count,
                "syllable_pattern": features.syllable_pattern,
                "phonological_complexity": features.phonological_complexity
            }
        except Exception:
            return None
    
    async def _get_morphological_info(self, shuar_text: str) -> dict:
        """Get morphological information for Shuar text."""
        try:
            # Try to find the word in database for morphological info
            word = await self.word_repository.find_by_shuar_text(shuar_text)
            
            if word and word.morphological_info:
                return {
                    "root_word": word.morphological_info.root_word,
                    "is_compound": word.morphological_info.is_compound,
                    "compound_components": word.morphological_info.compound_components,
                    "applied_suffixes": word.morphological_info.applied_suffixes,
                    "morphological_analysis": word.morphological_info.morphological_analysis
                }
            
            return None
        except Exception:
            return None
    
    async def _find_similar_words(
        self, 
        text: str, 
        language: Language, 
        max_results: int
    ) -> list[SimilarWord]:
        """Find similar words for suggestions."""
        try:
            if language == Language.SHUAR:
                # Find similar Shuar words
                candidate_words = await self.word_repository.search_similar_shuar_words(
                    text, similarity_threshold=0.3, limit=max_results * 2
                )
            else:
                # Find words with similar Spanish translations
                candidate_words = await self.word_repository.search_similar_spanish_words(
                    text, similarity_threshold=0.3, limit=max_results * 2
                )
            
            if not candidate_words:
                return []
            
            # Use similarity service to rank and filter
            criteria = SearchCriteria(
                min_similarity_threshold=0.3,
                max_results=max_results
            )
            
            similar_words = self.similarity_service.find_similar_words(
                text, candidate_words, criteria
            )
            
            return similar_words
            
        except Exception:
            return []