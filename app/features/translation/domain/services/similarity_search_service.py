"""Similarity search service for finding phonologically similar Shuar words."""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from app.features.translation.domain.entities.word import Word, VocalType
from app.features.translation.domain.value_objects.similarity_score import SimilarityScore
from app.features.translation.domain.value_objects.translation_result import SimilarWord
from app.features.translation.domain.services.phonological_analysis_service import PhonologicalAnalysisService
from app.core.shared.exceptions import ValidationError


@dataclass
class SearchCriteria:
    """Criteria for similarity search."""
    min_similarity_threshold: float = 0.3
    max_results: int = 10
    include_morphological: bool = True
    include_semantic: bool = False
    vocal_type_weight: float = 0.4
    phonological_weight: float = 0.4
    morphological_weight: float = 0.2


class SimilaritySearchService:
    """Domain service for finding similar words based on phonological and morphological features."""
    
    def __init__(self, phonological_service: PhonologicalAnalysisService):
        self.phonological_service = phonological_service
    
    def find_similar_words(
        self, 
        target_word: str, 
        candidate_words: List[Word],
        criteria: Optional[SearchCriteria] = None
    ) -> List[SimilarWord]:
        """Find words similar to the target word from a list of candidates."""
        if not target_word or not target_word.strip():
            raise ValidationError("Target word cannot be empty")
        
        if not candidate_words:
            return []
        
        criteria = criteria or SearchCriteria()
        target_word = target_word.lower().strip()
        
        # Analyze target word
        target_features = self.phonological_service.analyze_word(target_word)
        
        similar_words = []
        
        for candidate in candidate_words:
            # Skip exact matches
            if candidate.shuar_text.lower() == target_word:
                continue
            
            # Calculate similarity
            similarity = self._calculate_comprehensive_similarity(
                target_word, target_features, candidate, criteria
            )
            
            # Filter by threshold
            if similarity.overall_similarity >= criteria.min_similarity_threshold:
                explanation = self._generate_similarity_explanation(
                    target_word, candidate.shuar_text, similarity
                )
                
                similar_word = SimilarWord(
                    word=candidate,
                    similarity=similarity,
                    explanation=explanation
                )
                similar_words.append(similar_word)
        
        # Sort by similarity score (descending)
        similar_words.sort(
            key=lambda sw: sw.similarity.overall_similarity, 
            reverse=True
        )
        
        # Limit results
        return similar_words[:criteria.max_results]
    
    def find_similar_by_vocal_types(
        self, 
        target_vocal_types: List[VocalType], 
        candidate_words: List[Word],
        min_similarity: float = 0.5
    ) -> List[Word]:
        """Find words that share similar vocal type patterns."""
        if not target_vocal_types:
            return []
        
        target_set = set(target_vocal_types)
        similar_words = []
        
        for candidate in candidate_words:
            if not candidate.phonological_info:
                continue
            
            candidate_types = set(candidate.phonological_info.vocal_types_present)
            
            # Calculate Jaccard similarity for vocal types
            intersection = target_set & candidate_types
            union = target_set | candidate_types
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity >= min_similarity:
                    similar_words.append(candidate)
        
        return similar_words
    
    def find_similar_by_morphology(
        self, 
        target_word: Word, 
        candidate_words: List[Word],
        min_similarity: float = 0.5
    ) -> List[Word]:
        """Find words with similar morphological structure."""
        if not target_word.morphological_info:
            return []
        
        similar_words = []
        target_root = target_word.morphological_info.root_word
        target_suffixes = set(target_word.morphological_info.applied_suffixes)
        
        for candidate in candidate_words:
            if not candidate.morphological_info:
                continue
            
            similarity = self._calculate_morphological_similarity(
                target_root, target_suffixes, candidate
            )
            
            if similarity >= min_similarity:
                similar_words.append(candidate)
        
        return similar_words
    
    def find_rhyming_words(
        self, 
        target_word: str, 
        candidate_words: List[Word],
        min_syllables_match: int = 1
    ) -> List[Word]:
        """Find words that rhyme with the target word."""
        if not target_word:
            return []
        
        target_word = target_word.lower().strip()
        target_features = self.phonological_service.analyze_word(target_word)
        
        rhyming_words = []
        
        for candidate in candidate_words:
            candidate_features = self.phonological_service.analyze_word(candidate.shuar_text)
            
            # Simple rhyming: check if endings are similar
            rhyme_similarity = self._calculate_rhyme_similarity(
                target_word, candidate.shuar_text, 
                target_features, candidate_features,
                min_syllables_match
            )
            
            if rhyme_similarity > 0.6:
                rhyming_words.append(candidate)
        
        return rhyming_words
    
    def _calculate_comprehensive_similarity(
        self, 
        target_word: str, 
        target_features: Any,  # PhonologicalFeatures from phonological service
        candidate: Word,
        criteria: SearchCriteria
    ) -> SimilarityScore:
        """Calculate comprehensive similarity between target and candidate."""
        
        # Phonological similarity
        phonological_sim = self.phonological_service.calculate_phonological_similarity(
            target_word, candidate.shuar_text
        )
        
        # Morphological similarity
        morphological_sim = 0.5  # Default
        if criteria.include_morphological and candidate.morphological_info:
            morphological_sim = self._calculate_morphological_similarity_score(
                target_word, candidate
            )
        
        # Semantic similarity (placeholder - would need semantic analysis)
        semantic_sim = 0.5  # Default - would be calculated based on semantic vectors
        
        return SimilarityScore.create(
            phonological=phonological_sim,
            morphological=morphological_sim,
            semantic=semantic_sim
        )
    
    def _calculate_morphological_similarity_score(
        self, 
        target_word: str, 
        candidate: Word
    ) -> float:
        """Calculate morphological similarity score."""
        if not candidate.morphological_info:
            return 0.5
        
        # Analyze target word morphology (simplified)
        target_suffixes = self._extract_common_suffixes(target_word)
        candidate_suffixes = set(candidate.morphological_info.applied_suffixes)
        
        # Calculate suffix similarity
        if target_suffixes or candidate_suffixes:
            intersection = target_suffixes & candidate_suffixes
            union = target_suffixes | candidate_suffixes
            suffix_similarity = len(intersection) / len(union) if union else 0.0
        else:
            suffix_similarity = 0.5
        
        # Length similarity (morphologically complex words tend to be longer)
        target_len = len(target_word)
        candidate_len = len(candidate.shuar_text)
        max_len = max(target_len, candidate_len)
        length_similarity = 1.0 - abs(target_len - candidate_len) / max_len if max_len > 0 else 1.0
        
        return (suffix_similarity * 0.7 + length_similarity * 0.3)
    
    def _calculate_morphological_similarity(
        self, 
        target_root: str, 
        target_suffixes: set, 
        candidate: Word
    ) -> float:
        """Calculate morphological similarity between words."""
        if not candidate.morphological_info:
            return 0.0
        
        candidate_root = candidate.morphological_info.root_word
        candidate_suffixes = set(candidate.morphological_info.applied_suffixes)
        
        # Root similarity
        root_similarity = self.phonological_service.calculate_phonological_similarity(
            target_root, candidate_root
        )
        
        # Suffix similarity
        if target_suffixes or candidate_suffixes:
            intersection = target_suffixes & candidate_suffixes
            union = target_suffixes | candidate_suffixes
            suffix_similarity = len(intersection) / len(union) if union else 0.0
        else:
            suffix_similarity = 1.0  # Both have no suffixes
        
        return (root_similarity * 0.6 + suffix_similarity * 0.4)
    
    def _calculate_rhyme_similarity(
        self, 
        word1: str, 
        word2: str, 
        features1: Any, 
        features2: Any,
        min_syllables_match: int
    ) -> float:
        """Calculate rhyming similarity between words."""
        # Simple rhyming based on ending similarity
        min_len = min(len(word1), len(word2))
        max_match_len = min(min_len, min_syllables_match * 2)  # Approximate syllable length
        
        if max_match_len == 0:
            return 0.0
        
        # Check ending similarity
        ending1 = word1[-max_match_len:]
        ending2 = word2[-max_match_len:]
        
        # Calculate character-level similarity of endings
        matches = sum(1 for c1, c2 in zip(ending1, ending2) if c1 == c2)
        similarity = matches / max_match_len
        
        # Bonus for same syllable count
        if features1.syllable_count == features2.syllable_count:
            similarity += 0.2
        
        return min(1.0, similarity)
    
    def _extract_common_suffixes(self, word: str) -> set:
        """Extract common Shuar suffixes from a word (simplified)."""
        common_suffixes = {'-ni', '-ai', '-ka', '-ma', '-ta', '-nu', '-tu', '-chi', '-tsu'}
        found_suffixes = set()
        
        for suffix in common_suffixes:
            if word.endswith(suffix[1:]):  # Remove the '-' for matching
                found_suffixes.add(suffix)
        
        return found_suffixes
    
    def _generate_similarity_explanation(
        self, 
        target_word: str, 
        candidate_word: str, 
        similarity: SimilarityScore
    ) -> str:
        """Generate human-readable explanation of similarity."""
        explanations = []
        
        if similarity.phonological_similarity > 0.7:
            explanations.append("similar sound patterns")
        elif similarity.phonological_similarity > 0.5:
            explanations.append("some sound similarities")
        
        if similarity.morphological_similarity > 0.7:
            explanations.append("similar word structure")
        elif similarity.morphological_similarity > 0.5:
            explanations.append("related morphological patterns")
        
        if similarity.semantic_similarity > 0.7:
            explanations.append("related meaning")
        
        if not explanations:
            explanations.append("general linguistic patterns")
        
        level = similarity.get_similarity_level()
        base_explanation = f"{level.title()} similarity to '{target_word}'"
        
        if explanations:
            return f"{base_explanation}: {', '.join(explanations)}"
        else:
            return base_explanation
    
    def group_similar_words_by_pattern(
        self, 
        words: List[Word]
    ) -> Dict[str, List[Word]]:
        """Group words by similar phonological patterns."""
        pattern_groups = {}
        
        for word in words:
            if word.phonological_info:
                pattern = word.phonological_info.syllable_pattern
                vocal_types = tuple(sorted(word.phonological_info.vocal_types_present))
                
                # Create a pattern key
                pattern_key = f"{pattern}_{vocal_types}"
                
                if pattern_key not in pattern_groups:
                    pattern_groups[pattern_key] = []
                
                pattern_groups[pattern_key].append(word)
        
        return pattern_groups
    
    def find_minimal_pairs(
        self, 
        words: List[Word], 
        max_differences: int = 1
    ) -> List[Tuple[Word, Word]]:
        """Find minimal pairs (words that differ by only one phonological feature)."""
        minimal_pairs = []
        
        for i, word1 in enumerate(words):
            for word2 in words[i+1:]:
                differences = self._count_phonological_differences(word1, word2)
                
                if differences <= max_differences:
                    minimal_pairs.append((word1, word2))
        
        return minimal_pairs
    
    def _count_phonological_differences(self, word1: Word, word2: Word) -> int:
        """Count phonological differences between two words."""
        if not word1.phonological_info or not word2.phonological_info:
            return float('inf')  # Can't compare without phonological info
        
        differences = 0
        
        # Compare vocal types
        types1 = set(word1.phonological_info.vocal_types_present)
        types2 = set(word2.phonological_info.vocal_types_present)
        differences += len(types1.symmetric_difference(types2))
        
        # Compare syllable count
        if word1.phonological_info.number_of_syllables != word2.phonological_info.number_of_syllables:
            differences += 1
        
        # Compare IPA transcriptions (character-level differences)
        ipa1 = word1.phonological_info.ipa_transcription
        ipa2 = word2.phonological_info.ipa_transcription
        
        # Simple character difference count
        max_len = max(len(ipa1), len(ipa2))
        char_differences = sum(
            1 for i in range(max_len)
            if i >= len(ipa1) or i >= len(ipa2) or ipa1[i] != ipa2[i]
        )
        differences += char_differences
        
        return differences