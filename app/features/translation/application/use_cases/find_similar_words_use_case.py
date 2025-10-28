"""Use case for finding phonologically similar words."""

from typing import List, Optional
from dataclasses import dataclass

from app.features.translation.domain.entities.word import Word, VocalType
from app.features.translation.domain.entities.translation import Language
from app.features.translation.domain.value_objects.translation_result import SimilarWord
from app.features.translation.domain.services.similarity_search_service import SimilaritySearchService, SearchCriteria
from app.features.translation.domain.services.phonological_analysis_service import PhonologicalAnalysisService
from app.core.shared.repositories import IWordRepository
from app.core.shared.exceptions import ValidationError
from app.core.utils.validators import ShuarTextValidator, SpanishTextValidator


@dataclass
class FindSimilarWordsRequest:
    """Request for finding similar words."""
    word: str
    language: str  # "shuar" or "spanish"
    similarity_threshold: float = 0.3
    max_results: int = 10
    include_morphological: bool = True
    include_phonological: bool = True
    vocal_type_filter: Optional[List[str]] = None  # Filter by vocal types
    min_syllables: Optional[int] = None
    max_syllables: Optional[int] = None


class FindSimilarWordsUseCase:
    """Use case for finding words similar to a given word."""
    
    def __init__(
        self,
        word_repository: IWordRepository,
        similarity_service: SimilaritySearchService,
        phonological_service: PhonologicalAnalysisService
    ):
        self.word_repository = word_repository
        self.similarity_service = similarity_service
        self.phonological_service = phonological_service
    
    async def execute(self, request: FindSimilarWordsRequest) -> List[SimilarWord]:
        """Execute the find similar words use case."""
        # Validate input
        self._validate_request(request)
        
        # Normalize the input word
        normalized_word = self._normalize_word(request.word, request.language)
        
        # Get candidate words from repository
        candidate_words = await self._get_candidate_words(request, normalized_word)
        
        if not candidate_words:
            return []
        
        # Apply filters
        filtered_candidates = self._apply_filters(candidate_words, request)
        
        # Configure search criteria
        criteria = SearchCriteria(
            min_similarity_threshold=request.similarity_threshold,
            max_results=request.max_results,
            include_morphological=request.include_morphological,
            include_semantic=False  # Not implemented yet
        )
        
        # Find similar words using similarity service
        similar_words = self.similarity_service.find_similar_words(
            normalized_word, filtered_candidates, criteria
        )
        
        return similar_words
    
    def _validate_request(self, request: FindSimilarWordsRequest) -> None:
        """Validate the request parameters."""
        if not request.word or not request.word.strip():
            raise ValidationError("Word cannot be empty")
        
        if request.language.lower() not in ["shuar", "spanish"]:
            raise ValidationError("Language must be 'shuar' or 'spanish'")
        
        if not 0.0 <= request.similarity_threshold <= 1.0:
            raise ValidationError("Similarity threshold must be between 0.0 and 1.0")
        
        if request.max_results <= 0 or request.max_results > 50:
            raise ValidationError("Max results must be between 1 and 50")
        
        if request.vocal_type_filter:
            valid_types = {"oral", "nasal", "laryngealized"}
            for vocal_type in request.vocal_type_filter:
                if vocal_type.lower() not in valid_types:
                    raise ValidationError(f"Invalid vocal type: {vocal_type}")
        
        if request.min_syllables is not None and request.min_syllables < 1:
            raise ValidationError("Minimum syllables must be at least 1")
        
        if request.max_syllables is not None and request.max_syllables < 1:
            raise ValidationError("Maximum syllables must be at least 1")
        
        if (request.min_syllables is not None and 
            request.max_syllables is not None and 
            request.min_syllables > request.max_syllables):
            raise ValidationError("Minimum syllables cannot be greater than maximum syllables")
    
    def _normalize_word(self, word: str, language: str) -> str:
        """Normalize the word based on language."""
        if language.lower() == "shuar":
            return ShuarTextValidator.validate_shuar_text(word)
        else:
            return SpanishTextValidator.validate_spanish_text(word)
    
    async def _get_candidate_words(
        self, 
        request: FindSimilarWordsRequest, 
        normalized_word: str
    ) -> List[Word]:
        """Get candidate words from the repository."""
        if request.language.lower() == "shuar":
            # For Shuar words, get similar Shuar words
            candidates = await self.word_repository.search_similar_shuar_words(
                normalized_word, 
                similarity_threshold=0.1,  # Lower threshold to get more candidates
                limit=request.max_results * 3  # Get more candidates for filtering
            )
        else:
            # For Spanish words, find words with similar Spanish translations
            candidates = await self.word_repository.search_similar_spanish_words(
                normalized_word,
                similarity_threshold=0.1,
                limit=request.max_results * 3
            )
        
        return candidates
    
    def _apply_filters(
        self, 
        candidates: List[Word], 
        request: FindSimilarWordsRequest
    ) -> List[Word]:
        """Apply additional filters to candidate words."""
        filtered = candidates
        
        # Filter by vocal types if specified
        if request.vocal_type_filter:
            vocal_types = [VocalType(vt.lower()) for vt in request.vocal_type_filter]
            filtered = self._filter_by_vocal_types(filtered, vocal_types)
        
        # Filter by syllable count if specified
        if request.min_syllables is not None or request.max_syllables is not None:
            filtered = self._filter_by_syllable_count(
                filtered, request.min_syllables, request.max_syllables
            )
        
        return filtered
    
    def _filter_by_vocal_types(
        self, 
        words: List[Word], 
        vocal_types: List[VocalType]
    ) -> List[Word]:
        """Filter words by vocal types present."""
        filtered_words = []
        
        for word in words:
            if word.phonological_info:
                word_vocal_types = set(word.phonological_info.vocal_types_present)
                required_types = set(vocal_types)
                
                # Check if word contains any of the required vocal types
                if word_vocal_types & required_types:
                    filtered_words.append(word)
            elif not vocal_types:  # If no vocal types required and word has no info
                filtered_words.append(word)
        
        return filtered_words
    
    def _filter_by_syllable_count(
        self, 
        words: List[Word], 
        min_syllables: Optional[int], 
        max_syllables: Optional[int]
    ) -> List[Word]:
        """Filter words by syllable count."""
        filtered_words = []
        
        for word in words:
            syllable_count = None
            
            if word.phonological_info:
                syllable_count = word.phonological_info.number_of_syllables
            else:
                # Estimate syllable count if phonological info not available
                try:
                    features = self.phonological_service.analyze_word(word.shuar_text)
                    syllable_count = features.syllable_count
                except:
                    continue  # Skip words we can't analyze
            
            if syllable_count is not None:
                if min_syllables is not None and syllable_count < min_syllables:
                    continue
                if max_syllables is not None and syllable_count > max_syllables:
                    continue
                
                filtered_words.append(word)
        
        return filtered_words


@dataclass
class FindRhymingWordsRequest:
    """Request for finding rhyming words."""
    word: str
    language: str = "shuar"
    min_syllables_match: int = 1
    max_results: int = 10


class FindRhymingWordsUseCase:
    """Use case for finding words that rhyme with a given word."""
    
    def __init__(
        self,
        word_repository: IWordRepository,
        similarity_service: SimilaritySearchService
    ):
        self.word_repository = word_repository
        self.similarity_service = similarity_service
    
    async def execute(self, request: FindRhymingWordsRequest) -> List[Word]:
        """Execute the find rhyming words use case."""
        # Validate input
        if not request.word or not request.word.strip():
            raise ValidationError("Word cannot be empty")
        
        if request.language.lower() not in ["shuar", "spanish"]:
            raise ValidationError("Language must be 'shuar' or 'spanish'")
        
        # Normalize word
        normalized_word = request.word.lower().strip()
        
        # Get candidate words
        if request.language.lower() == "shuar":
            candidates = await self.word_repository.search_similar_shuar_words(
                normalized_word, similarity_threshold=0.1, limit=100
            )
        else:
            candidates = await self.word_repository.search_similar_spanish_words(
                normalized_word, similarity_threshold=0.1, limit=100
            )
        
        # Find rhyming words
        rhyming_words = self.similarity_service.find_rhyming_words(
            normalized_word, candidates, request.min_syllables_match
        )
        
        # Limit results
        return rhyming_words[:request.max_results]


@dataclass
class FindMinimalPairsRequest:
    """Request for finding minimal pairs."""
    word: str
    language: str = "shuar"
    max_differences: int = 1
    max_results: int = 10


class FindMinimalPairsUseCase:
    """Use case for finding minimal pairs (words differing by one phonological feature)."""
    
    def __init__(
        self,
        word_repository: IWordRepository,
        similarity_service: SimilaritySearchService
    ):
        self.word_repository = word_repository
        self.similarity_service = similarity_service
    
    async def execute(self, request: FindMinimalPairsRequest) -> List[Word]:
        """Execute the find minimal pairs use case."""
        # Validate input
        if not request.word or not request.word.strip():
            raise ValidationError("Word cannot be empty")
        
        # Get candidate words (high similarity threshold for minimal pairs)
        if request.language.lower() == "shuar":
            candidates = await self.word_repository.search_similar_shuar_words(
                request.word, similarity_threshold=0.6, limit=50
            )
        else:
            candidates = await self.word_repository.search_similar_spanish_words(
                request.word, similarity_threshold=0.6, limit=50
            )
        
        # Find the target word in database
        target_word = None
        if request.language.lower() == "shuar":
            target_word = await self.word_repository.find_by_shuar_text(request.word)
        
        if not target_word:
            # Create a temporary word for comparison
            from app.features.translation.domain.entities.word import Word
            target_word = Word(shuar_text=request.word, spanish_translation="")
        
        # Add target word to candidates for comparison
        all_words = [target_word] + candidates
        
        # Find minimal pairs
        minimal_pairs = self.similarity_service.find_minimal_pairs(
            all_words, request.max_differences
        )
        
        # Extract pairs that include the target word
        result_words = []
        for word1, word2 in minimal_pairs:
            if word1.shuar_text.lower() == request.word.lower():
                result_words.append(word2)
            elif word2.shuar_text.lower() == request.word.lower():
                result_words.append(word1)
        
        # Remove duplicates and limit results
        seen = set()
        unique_words = []
        for word in result_words:
            if word.shuar_text not in seen:
                seen.add(word.shuar_text)
                unique_words.append(word)
        
        return unique_words[:request.max_results]