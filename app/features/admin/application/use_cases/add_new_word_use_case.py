"""Use case for adding new words to the vocabulary database."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from uuid import UUID

from app.features.translation.domain.entities.word import Word, WordType, PhonologicalInfo, MorphologicalInfo
from app.features.translation.domain.services.phonological_analysis_service import PhonologicalAnalysisService
from app.core.shared.repositories import IWordRepository
from app.core.shared.exceptions import ValidationError
from app.core.utils.validators import ShuarTextValidator, SpanishTextValidator


@dataclass
class AddNewWordRequest:
    """Request for adding a new word to the vocabulary."""
    shuar_text: str
    spanish_translation: str
    word_type: Optional[str] = None  # "noun", "verb", "adjective", etc.
    definition_extended: Optional[str] = None
    
    # Phonological information
    ipa_transcription: Optional[str] = None
    vocal_types: Optional[List[str]] = None  # ["oral", "nasal", "laryngealized"]
    
    # Morphological information
    root_word: Optional[str] = None
    is_compound: bool = False
    compound_components: Optional[List[str]] = None
    applied_suffixes: Optional[List[str]] = None
    morphological_analysis: Optional[str] = None
    
    # Usage and examples
    usage_examples: Optional[List[Dict[str, str]]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None
    cultural_notes: Optional[str] = None
    dialect_variations: Optional[List[Dict[str, str]]] = None
    
    # Metadata
    created_by: Optional[UUID] = None
    confidence_level: float = 0.8  # Higher for expert-added words
    is_verified: bool = True  # Expert-added words are pre-verified


class AddNewWordUseCase:
    """Use case for experts to add new words to the vocabulary database."""
    
    def __init__(
        self,
        word_repository: IWordRepository,
        phonological_service: PhonologicalAnalysisService
    ):
        self.word_repository = word_repository
        self.phonological_service = phonological_service
    
    async def execute(self, request: AddNewWordRequest) -> Word:
        """Execute the add new word use case."""
        # Validate request
        await self._validate_request(request)
        
        # Check if word already exists
        existing_word = await self.word_repository.find_by_shuar_text(request.shuar_text)
        if existing_word:
            raise ValidationError(f"Word '{request.shuar_text}' already exists in the database")
        
        # Create phonological information
        phonological_info = self._create_phonological_info(request)
        
        # Create morphological information
        morphological_info = self._create_morphological_info(request)
        
        # Create word entity
        word = Word(
            shuar_text=request.shuar_text,
            spanish_translation=request.spanish_translation,
            word_type=WordType(request.word_type.lower()) if request.word_type else None,
            phonological_info=phonological_info,
            morphological_info=morphological_info,
            definition_extended=request.definition_extended,
            usage_examples=request.usage_examples or [],
            synonyms=request.synonyms or [],
            antonyms=request.antonyms or [],
            cultural_notes=request.cultural_notes,
            dialect_variations=request.dialect_variations or [],
            confidence_level=request.confidence_level,
            is_verified=request.is_verified
        )
        
        # Save word
        saved_word = await self.word_repository.save(word)
        
        return saved_word
    
    async def _validate_request(self, request: AddNewWordRequest) -> None:
        """Validate the add word request."""
        # Validate required fields
        if not request.shuar_text or not request.shuar_text.strip():
            raise ValidationError("Shuar text is required")
        
        if not request.spanish_translation or not request.spanish_translation.strip():
            raise ValidationError("Spanish translation is required")
        
        # Validate Shuar text
        try:
            ShuarTextValidator.validate_shuar_text(request.shuar_text)
        except ValidationError as e:
            raise ValidationError(f"Invalid Shuar text: {e.message}")
        
        # Validate Spanish translation
        try:
            SpanishTextValidator.validate_spanish_text(request.spanish_translation)
        except ValidationError as e:
            raise ValidationError(f"Invalid Spanish translation: {e.message}")
        
        # Validate word type
        if request.word_type:
            valid_types = {"noun", "verb", "adjective", "adverb", "pronoun", "conjunction", "preposition", "interjection"}
            if request.word_type.lower() not in valid_types:
                raise ValidationError(f"Invalid word type: {request.word_type}")
        
        # Validate vocal types
        if request.vocal_types:
            valid_vocal_types = {"oral", "nasal", "laryngealized"}
            for vocal_type in request.vocal_types:
                if vocal_type.lower() not in valid_vocal_types:
                    raise ValidationError(f"Invalid vocal type: {vocal_type}")
        
        # Validate confidence level
        if not 0.0 <= request.confidence_level <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
        
        # Validate text lengths
        if request.definition_extended and len(request.definition_extended) > 2000:
            raise ValidationError("Extended definition exceeds maximum length of 2000 characters")
        
        if request.cultural_notes and len(request.cultural_notes) > 1000:
            raise ValidationError("Cultural notes exceed maximum length of 1000 characters")
        
        if request.morphological_analysis and len(request.morphological_analysis) > 500:
            raise ValidationError("Morphological analysis exceeds maximum length of 500 characters")
        
        # Validate compound word requirements
        if request.is_compound:
            if not request.compound_components or len(request.compound_components) < 2:
                raise ValidationError("Compound words must have at least 2 components")
    
    def _create_phonological_info(self, request: AddNewWordRequest) -> Optional[PhonologicalInfo]:
        """Create phonological information for the word."""
        try:
            # Use provided IPA transcription or generate it
            ipa_transcription = request.ipa_transcription
            if not ipa_transcription:
                ipa_transcription = self.phonological_service.generate_ipa_transcription(
                    request.shuar_text
                )
            
            # Analyze phonological features
            features = self.phonological_service.analyze_word(request.shuar_text)
            
            # Use provided vocal types or detected ones
            vocal_types_present = []
            if request.vocal_types:
                from app.features.translation.domain.entities.word import VocalType
                vocal_types_present = [VocalType(vt.lower()) for vt in request.vocal_types]
            else:
                vocal_types_present = list(features.vocal_types)
            
            return PhonologicalInfo(
                ipa_transcription=ipa_transcription,
                has_nasal_vowels=any(vt.value == "nasal" for vt in vocal_types_present),
                has_laryngealized_vowels=any(vt.value == "laryngealized" for vt in vocal_types_present),
                vocal_types_present=vocal_types_present,
                number_of_syllables=features.syllable_count,
                syllable_pattern=features.syllable_pattern
            )
            
        except Exception:
            # If phonological analysis fails, return None
            return None
    
    def _create_morphological_info(self, request: AddNewWordRequest) -> Optional[MorphologicalInfo]:
        """Create morphological information for the word."""
        if not any([
            request.root_word,
            request.is_compound,
            request.compound_components,
            request.applied_suffixes,
            request.morphological_analysis
        ]):
            return None
        
        # Use provided root word or default to the word itself
        root_word = request.root_word or request.shuar_text
        
        return MorphologicalInfo(
            root_word=root_word,
            is_compound=request.is_compound,
            compound_components=request.compound_components or [],
            applied_suffixes=request.applied_suffixes or [],
            morphological_analysis=request.morphological_analysis
        )


@dataclass
class BulkImportWordsRequest:
    """Request for bulk importing words from external data."""
    words_data: List[Dict[str, Any]]
    created_by: UUID
    validate_phonology: bool = True
    skip_duplicates: bool = True
    batch_size: int = 100


class BulkImportWordsUseCase:
    """Use case for bulk importing words from existing linguistic data."""
    
    def __init__(
        self,
        word_repository: IWordRepository,
        phonological_service: PhonologicalAnalysisService,
        add_word_use_case: AddNewWordUseCase
    ):
        self.word_repository = word_repository
        self.phonological_service = phonological_service
        self.add_word_use_case = add_word_use_case
    
    async def execute(self, request: BulkImportWordsRequest) -> Dict[str, Any]:
        """Execute the bulk import use case."""
        results = {
            "total_processed": 0,
            "successful_imports": 0,
            "skipped_duplicates": 0,
            "failed_imports": 0,
            "errors": []
        }
        
        # Process words in batches
        for i in range(0, len(request.words_data), request.batch_size):
            batch = request.words_data[i:i + request.batch_size]
            batch_results = await self._process_batch(batch, request)
            
            # Aggregate results
            results["total_processed"] += batch_results["total_processed"]
            results["successful_imports"] += batch_results["successful_imports"]
            results["skipped_duplicates"] += batch_results["skipped_duplicates"]
            results["failed_imports"] += batch_results["failed_imports"]
            results["errors"].extend(batch_results["errors"])
        
        return results
    
    async def _process_batch(
        self, 
        batch: List[Dict[str, Any]], 
        request: BulkImportWordsRequest
    ) -> Dict[str, Any]:
        """Process a batch of words for import."""
        batch_results = {
            "total_processed": 0,
            "successful_imports": 0,
            "skipped_duplicates": 0,
            "failed_imports": 0,
            "errors": []
        }
        
        words_to_save = []
        
        for word_data in batch:
            batch_results["total_processed"] += 1
            
            try:
                # Convert dict to AddNewWordRequest
                add_request = self._convert_to_add_request(word_data, request.created_by)
                
                # Check for duplicates if requested
                if request.skip_duplicates:
                    existing = await self.word_repository.find_by_shuar_text(add_request.shuar_text)
                    if existing:
                        batch_results["skipped_duplicates"] += 1
                        continue
                
                # Validate and create word
                word = await self._create_word_from_request(add_request, request.validate_phonology)
                words_to_save.append(word)
                
            except Exception as e:
                batch_results["failed_imports"] += 1
                batch_results["errors"].append({
                    "word_data": word_data,
                    "error": str(e)
                })
        
        # Bulk save successful words
        if words_to_save:
            try:
                saved_words = await self.word_repository.bulk_save(words_to_save)
                batch_results["successful_imports"] += len(saved_words)
            except Exception as e:
                # If bulk save fails, try individual saves
                for word in words_to_save:
                    try:
                        await self.word_repository.save(word)
                        batch_results["successful_imports"] += 1
                    except Exception as individual_error:
                        batch_results["failed_imports"] += 1
                        batch_results["errors"].append({
                            "word": word.shuar_text,
                            "error": str(individual_error)
                        })
        
        return batch_results
    
    def _convert_to_add_request(self, word_data: Dict[str, Any], created_by: UUID) -> AddNewWordRequest:
        """Convert dictionary data to AddNewWordRequest."""
        return AddNewWordRequest(
            shuar_text=word_data.get("shuar_text", ""),
            spanish_translation=word_data.get("spanish_translation", ""),
            word_type=word_data.get("word_type"),
            definition_extended=word_data.get("definition_extended"),
            ipa_transcription=word_data.get("ipa_transcription"),
            vocal_types=word_data.get("vocal_types"),
            root_word=word_data.get("root_word"),
            is_compound=word_data.get("is_compound", False),
            compound_components=word_data.get("compound_components"),
            applied_suffixes=word_data.get("applied_suffixes"),
            morphological_analysis=word_data.get("morphological_analysis"),
            usage_examples=word_data.get("usage_examples"),
            synonyms=word_data.get("synonyms"),
            antonyms=word_data.get("antonyms"),
            cultural_notes=word_data.get("cultural_notes"),
            dialect_variations=word_data.get("dialect_variations"),
            created_by=created_by,
            confidence_level=word_data.get("confidence_level", 0.7),
            is_verified=word_data.get("is_verified", False)
        )
    
    async def _create_word_from_request(
        self, 
        request: AddNewWordRequest, 
        validate_phonology: bool
    ) -> Word:
        """Create a word entity from the request without saving it."""
        # Basic validation
        if not request.shuar_text or not request.spanish_translation:
            raise ValidationError("Both Shuar text and Spanish translation are required")
        
        # Phonological validation if requested
        if validate_phonology:
            try:
                ShuarTextValidator.validate_shuar_text(request.shuar_text)
            except ValidationError as e:
                raise ValidationError(f"Invalid Shuar text '{request.shuar_text}': {e.message}")
        
        # Create phonological info
        phonological_info = None
        try:
            if validate_phonology:
                phonological_info = self.add_word_use_case._create_phonological_info(request)
        except Exception:
            pass  # Continue without phonological info if analysis fails
        
        # Create morphological info
        morphological_info = self.add_word_use_case._create_morphological_info(request)
        
        # Create word entity
        word = Word(
            shuar_text=request.shuar_text,
            spanish_translation=request.spanish_translation,
            word_type=WordType(request.word_type.lower()) if request.word_type else None,
            phonological_info=phonological_info,
            morphological_info=morphological_info,
            definition_extended=request.definition_extended,
            usage_examples=request.usage_examples or [],
            synonyms=request.synonyms or [],
            antonyms=request.antonyms or [],
            cultural_notes=request.cultural_notes,
            dialect_variations=request.dialect_variations or [],
            confidence_level=request.confidence_level,
            is_verified=request.is_verified
        )
        
        return word