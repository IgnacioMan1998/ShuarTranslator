"""Use case for getting translation with complete phonetic and morphological analysis."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.features.translation.domain.entities.word import Word
from app.features.translation.domain.entities.translation import Translation, Language
from app.features.translation.domain.services.phonological_analysis_service import PhonologicalAnalysisService
from app.features.translation.domain.services.translation_scoring_service import TranslationScoringService
from app.core.shared.repositories import IWordRepository, ITranslationRepository, IFeedbackRepository
from app.core.shared.exceptions import ValidationError, NotFoundError


@dataclass
class GetTranslationWithPhoneticsRequest:
    """Request for getting detailed translation with phonetics."""
    word: str
    source_language: str  # "shuar" or "spanish"
    include_alternatives: bool = True
    include_usage_examples: bool = True
    include_cultural_notes: bool = True
    include_quality_metrics: bool = True


@dataclass
class DetailedTranslationResponse:
    """Detailed translation response with phonetic and morphological information."""
    source_word: Dict[str, Any]
    primary_translation: Dict[str, Any]
    alternative_translations: List[Dict[str, Any]]
    phonetic_analysis: Optional[Dict[str, Any]]
    morphological_analysis: Optional[Dict[str, Any]]
    usage_examples: List[Dict[str, Any]]
    cultural_notes: Optional[str]
    quality_metrics: Optional[Dict[str, Any]]
    related_words: List[Dict[str, Any]]


class GetTranslationWithPhoneticsUseCase:
    """Use case for getting comprehensive translation information with phonetic analysis."""
    
    def __init__(
        self,
        word_repository: IWordRepository,
        translation_repository: ITranslationRepository,
        feedback_repository: IFeedbackRepository,
        phonological_service: PhonologicalAnalysisService,
        scoring_service: TranslationScoringService
    ):
        self.word_repository = word_repository
        self.translation_repository = translation_repository
        self.feedback_repository = feedback_repository
        self.phonological_service = phonological_service
        self.scoring_service = scoring_service
    
    async def execute(self, request: GetTranslationWithPhoneticsRequest) -> DetailedTranslationResponse:
        """Execute the detailed translation use case."""
        # Validate input
        self._validate_request(request)
        
        # Find the source word
        source_word = await self._find_source_word(request.word, request.source_language)
        if not source_word:
            raise NotFoundError(f"Word '{request.word}' not found in {request.source_language}")
        
        # Get translations
        translations = await self._get_translations(source_word, request.source_language)
        
        if not translations:
            raise NotFoundError(f"No translations found for '{request.word}'")
        
        # Select primary translation (highest quality)
        primary_translation = translations[0]
        alternative_translations = translations[1:] if request.include_alternatives else []
        
        # Get phonetic analysis (for Shuar words)
        phonetic_analysis = None
        if request.source_language.lower() == "shuar":
            phonetic_analysis = await self._get_phonetic_analysis(source_word)
        
        # Get morphological analysis
        morphological_analysis = await self._get_morphological_analysis(source_word)
        
        # Get usage examples
        usage_examples = []
        if request.include_usage_examples:
            usage_examples = self._get_usage_examples(source_word)
        
        # Get cultural notes
        cultural_notes = None
        if request.include_cultural_notes:
            cultural_notes = source_word.cultural_notes
        
        # Get quality metrics
        quality_metrics = None
        if request.include_quality_metrics:
            quality_metrics = await self._get_quality_metrics(primary_translation, source_word)
        
        # Get related words
        related_words = await self._get_related_words(source_word)
        
        return DetailedTranslationResponse(
            source_word=self._format_word_info(source_word),
            primary_translation=self._format_translation_info(primary_translation),
            alternative_translations=[
                self._format_translation_info(t) for t in alternative_translations
            ],
            phonetic_analysis=phonetic_analysis,
            morphological_analysis=morphological_analysis,
            usage_examples=usage_examples,
            cultural_notes=cultural_notes,
            quality_metrics=quality_metrics,
            related_words=[self._format_word_info(w) for w in related_words]
        )
    
    def _validate_request(self, request: GetTranslationWithPhoneticsRequest) -> None:
        """Validate the request parameters."""
        if not request.word or not request.word.strip():
            raise ValidationError("Word cannot be empty")
        
        if request.source_language.lower() not in ["shuar", "spanish"]:
            raise ValidationError("Source language must be 'shuar' or 'spanish'")
    
    async def _find_source_word(self, word: str, language: str) -> Optional[Word]:
        """Find the source word in the repository."""
        normalized_word = word.lower().strip()
        
        if language.lower() == "shuar":
            return await self.word_repository.find_by_shuar_text(normalized_word)
        else:
            # For Spanish, find words with this Spanish translation
            words = await self.word_repository.find_by_spanish_translation(normalized_word)
            return words[0] if words else None
    
    async def _get_translations(self, source_word: Word, source_language: str) -> List[Translation]:
        """Get all translations for the source word."""
        if source_language.lower() == "shuar":
            source_lang = Language.SHUAR
            target_lang = Language.SPANISH
            source_text = source_word.shuar_text
        else:
            source_lang = Language.SPANISH
            target_lang = Language.SHUAR
            source_text = source_word.spanish_translation
        
        translations = await self.translation_repository.find_by_source_text(
            source_text, source_lang
        )
        
        # Filter by target language and approved status
        filtered_translations = [
            t for t in translations 
            if t.target_language == target_lang and 
            t.status.value in ["approved", "pending"]
        ]
        
        # Sort by quality (confidence, rating, usage)
        filtered_translations.sort(
            key=lambda t: (t.confidence_score, t.average_rating, t.usage_count),
            reverse=True
        )
        
        return filtered_translations
    
    async def _get_phonetic_analysis(self, word: Word) -> Optional[Dict[str, Any]]:
        """Get detailed phonetic analysis for a Shuar word."""
        try:
            # Use existing phonological info if available
            if word.phonological_info:
                return {
                    "ipa_transcription": word.phonological_info.ipa_transcription,
                    "vocal_types": [vt.value for vt in word.phonological_info.vocal_types_present],
                    "has_nasal_vowels": word.phonological_info.has_nasal_vowels,
                    "has_laryngealized_vowels": word.phonological_info.has_laryngealized_vowels,
                    "syllable_count": word.phonological_info.number_of_syllables,
                    "syllable_pattern": word.phonological_info.syllable_pattern
                }
            
            # Generate analysis if not available
            features = self.phonological_service.analyze_word(word.shuar_text)
            ipa_transcription = self.phonological_service.generate_ipa_transcription(word.shuar_text)
            
            return {
                "ipa_transcription": ipa_transcription,
                "vocal_types": [vt.value for vt in features.vocal_types],
                "has_nasal_vowels": VocalType.NASAL in features.vocal_types,
                "has_laryngealized_vowels": VocalType.LARYNGEALIZED in features.vocal_types,
                "syllable_count": features.syllable_count,
                "syllable_pattern": features.syllable_pattern,
                "phonological_complexity": features.phonological_complexity,
                "digraphs_present": features.digraphs_present,
                "consonant_clusters": features.consonant_clusters
            }
            
        except Exception:
            return None
    
    async def _get_morphological_analysis(self, word: Word) -> Optional[Dict[str, Any]]:
        """Get morphological analysis for the word."""
        if not word.morphological_info:
            return None
        
        return {
            "root_word": word.morphological_info.root_word,
            "is_compound": word.morphological_info.is_compound,
            "compound_components": word.morphological_info.compound_components,
            "applied_suffixes": word.morphological_info.applied_suffixes,
            "morphological_analysis": word.morphological_info.morphological_analysis
        }
    
    def _get_usage_examples(self, word: Word) -> List[Dict[str, Any]]:
        """Get usage examples for the word."""
        return word.usage_examples or []
    
    async def _get_quality_metrics(
        self, 
        translation: Translation, 
        source_word: Word
    ) -> Dict[str, Any]:
        """Get quality metrics for the translation."""
        try:
            # Get feedback for this translation
            feedback_list = await self.feedback_repository.find_by_translation_id(translation.id)
            
            # Calculate quality metrics
            quality_metrics = self.scoring_service.calculate_quality_metrics(
                translation, feedback_list, source_word
            )
            
            return {
                "confidence_score": quality_metrics.confidence_score,
                "community_rating": quality_metrics.community_rating,
                "expert_approval": quality_metrics.expert_approval,
                "usage_frequency": quality_metrics.usage_frequency,
                "feedback_count": quality_metrics.feedback_count,
                "native_speaker_approval": quality_metrics.native_speaker_approval,
                "phonological_accuracy": quality_metrics.phonological_accuracy,
                "cultural_appropriateness": quality_metrics.cultural_appropriateness,
                "overall_quality_score": quality_metrics.overall_quality_score
            }
            
        except Exception:
            return {
                "confidence_score": translation.confidence_score,
                "community_rating": translation.average_rating,
                "usage_frequency": translation.usage_count,
                "expert_approval": translation.approved_by is not None
            }
    
    async def _get_related_words(self, word: Word) -> List[Word]:
        """Get words related to the source word."""
        related_words = []
        
        try:
            # Get words with same root (if morphological info available)
            if word.morphological_info and word.morphological_info.root_word:
                root_words = await self.word_repository.find_by_root_word(
                    word.morphological_info.root_word
                )
                related_words.extend(root_words[:3])  # Limit to 3
            
            # Get synonyms
            if word.synonyms:
                for synonym in word.synonyms[:3]:  # Limit to 3
                    synonym_word = await self.word_repository.find_by_shuar_text(synonym)
                    if synonym_word:
                        related_words.append(synonym_word)
            
            # Get antonyms
            if word.antonyms:
                for antonym in word.antonyms[:2]:  # Limit to 2
                    antonym_word = await self.word_repository.find_by_shuar_text(antonym)
                    if antonym_word:
                        related_words.append(antonym_word)
            
            # Remove duplicates and the original word
            unique_related = []
            seen_ids = {word.id}
            
            for related_word in related_words:
                if related_word.id not in seen_ids:
                    seen_ids.add(related_word.id)
                    unique_related.append(related_word)
            
            return unique_related[:5]  # Limit total to 5
            
        except Exception:
            return []
    
    def _format_word_info(self, word: Word) -> Dict[str, Any]:
        """Format word information for response."""
        return {
            "id": str(word.id),
            "shuar_text": word.shuar_text,
            "spanish_translation": word.spanish_translation,
            "word_type": word.word_type.value if word.word_type else None,
            "definition_extended": word.definition_extended,
            "frequency_score": word.frequency_score,
            "confidence_level": word.confidence_level,
            "is_verified": word.is_verified,
            "synonyms": word.synonyms,
            "antonyms": word.antonyms
        }
    
    def _format_translation_info(self, translation: Translation) -> Dict[str, Any]:
        """Format translation information for response."""
        return {
            "id": str(translation.id),
            "source_text": translation.source_text,
            "target_text": translation.target_text,
            "confidence_score": translation.confidence_score,
            "average_rating": translation.average_rating,
            "total_ratings": translation.total_ratings,
            "usage_count": translation.usage_count,
            "status": translation.status.value,
            "context": translation.context.to_dict() if translation.context else None,
            "created_at": translation.created_at.isoformat(),
            "approved_at": translation.approved_at.isoformat() if translation.approved_at else None
        }