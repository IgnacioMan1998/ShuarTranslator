"""Phonological analysis service for Shuar language processing."""

from typing import List, Dict, Any, Set, Optional
import re
from dataclasses import dataclass

from app.features.translation.domain.entities.word import VocalType, PhonologicalInfo
from app.features.translation.domain.value_objects.similarity_score import SimilarityScore
from app.core.shared.exceptions import ValidationError


@dataclass
class PhonologicalFeatures:
    """Phonological features of a Shuar word."""
    vocal_types: Set[VocalType]
    has_digraphs: bool
    digraphs_present: List[str]
    consonant_clusters: List[str]
    syllable_count: int
    syllable_pattern: str
    phonological_complexity: float


class PhonologicalAnalysisService:
    """Domain service for analyzing Shuar phonological features."""
    
    # Shuar phonological inventory
    ORAL_VOWELS = {'a', 'e', 'i', 'u'}
    NASAL_VOWELS = {'á', 'é', 'í', 'ú'}
    LARYNGEALIZED_VOWELS = {'ä', 'ë', 'ï', 'ü'}
    ALL_VOWELS = ORAL_VOWELS | NASAL_VOWELS | LARYNGEALIZED_VOWELS
    
    CONSONANTS = {'p', 't', 'k', 's', 'j', 'm', 'n', 'r', 'w', 'y'}
    DIGRAPHS = {'ch', 'sh', 'ts'}
    
    # IPA mappings for Shuar sounds
    IPA_MAPPINGS = {
        # Oral vowels
        'a': 'a', 'e': 'e', 'i': 'i', 'u': 'u',
        # Nasal vowels
        'á': 'ã', 'é': 'ẽ', 'í': 'ĩ', 'ú': 'ũ',
        # Laryngealized vowels
        'ä': 'aʔ', 'ë': 'eʔ', 'ï': 'iʔ', 'ü': 'uʔ',
        # Consonants
        'p': 'p', 't': 't', 'k': 'k', 's': 's', 'j': 'h',
        'm': 'm', 'n': 'n', 'r': 'ɾ', 'w': 'w', 'y': 'j',
        # Digraphs
        'ch': 'tʃ', 'sh': 'ʃ', 'ts': 'ts'
    }
    
    def analyze_word(self, shuar_word: str) -> PhonologicalFeatures:
        """Analyze the phonological features of a Shuar word."""
        if not shuar_word or not shuar_word.strip():
            raise ValidationError("Word cannot be empty")
        
        word = shuar_word.lower().strip()
        
        # Detect vocal types
        vocal_types = self._detect_vocal_types(word)
        
        # Detect digraphs
        digraphs_present = self._detect_digraphs(word)
        has_digraphs = len(digraphs_present) > 0
        
        # Detect consonant clusters
        consonant_clusters = self._detect_consonant_clusters(word)
        
        # Count syllables
        syllable_count = self._count_syllables(word)
        
        # Determine syllable pattern
        syllable_pattern = self._analyze_syllable_pattern(word)
        
        # Calculate phonological complexity
        complexity = self._calculate_phonological_complexity(
            vocal_types, digraphs_present, consonant_clusters, syllable_count
        )
        
        return PhonologicalFeatures(
            vocal_types=vocal_types,
            has_digraphs=has_digraphs,
            digraphs_present=digraphs_present,
            consonant_clusters=consonant_clusters,
            syllable_count=syllable_count,
            syllable_pattern=syllable_pattern,
            phonological_complexity=complexity
        )
    
    def _detect_vocal_types(self, word: str) -> Set[VocalType]:
        """Detect which types of vowels are present in the word."""
        vocal_types = set()
        
        for char in word:
            if char in self.ORAL_VOWELS:
                vocal_types.add(VocalType.ORAL)
            elif char in self.NASAL_VOWELS:
                vocal_types.add(VocalType.NASAL)
            elif char in self.LARYNGEALIZED_VOWELS:
                vocal_types.add(VocalType.LARYNGEALIZED)
        
        return vocal_types
    
    def _detect_digraphs(self, word: str) -> List[str]:
        """Detect digraphs present in the word."""
        digraphs_found = []
        
        for digraph in self.DIGRAPHS:
            if digraph in word:
                # Count occurrences
                count = word.count(digraph)
                digraphs_found.extend([digraph] * count)
        
        return digraphs_found
    
    def _detect_consonant_clusters(self, word: str) -> List[str]:
        """Detect consonant clusters in the word."""
        # Replace digraphs with single characters for analysis
        temp_word = word
        for digraph in self.DIGRAPHS:
            temp_word = temp_word.replace(digraph, 'X')
        
        clusters = []
        current_cluster = ""
        
        for char in temp_word:
            if char in self.CONSONANTS or char == 'X':
                current_cluster += char
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = ""
        
        # Check final cluster
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        
        return clusters
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a Shuar word based on vowel nuclei."""
        # Replace digraphs to avoid counting them as separate sounds
        temp_word = word
        for digraph in self.DIGRAPHS:
            temp_word = temp_word.replace(digraph, 'X')
        
        vowel_count = 0
        prev_was_vowel = False
        
        for char in temp_word:
            is_vowel = char in self.ALL_VOWELS
            
            if is_vowel and not prev_was_vowel:
                vowel_count += 1
            
            prev_was_vowel = is_vowel
        
        return max(1, vowel_count)  # At least one syllable
    
    def _analyze_syllable_pattern(self, word: str) -> str:
        """Analyze the syllable pattern (CV, CVC, etc.)."""
        # Replace digraphs with single characters
        temp_word = word
        for digraph in self.DIGRAPHS:
            temp_word = temp_word.replace(digraph, 'X')
        
        pattern = ""
        for char in temp_word:
            if char in self.ALL_VOWELS:
                pattern += "V"
            elif char in self.CONSONANTS or char == 'X':
                pattern += "C"
        
        return pattern
    
    def _calculate_phonological_complexity(
        self, 
        vocal_types: Set[VocalType], 
        digraphs: List[str], 
        clusters: List[str], 
        syllable_count: int
    ) -> float:
        """Calculate phonological complexity score (0.0 to 1.0)."""
        complexity = 0.0
        
        # Base complexity from syllable count
        complexity += min(syllable_count * 0.1, 0.3)
        
        # Vocal type diversity
        complexity += len(vocal_types) * 0.1
        
        # Digraph presence
        complexity += len(digraphs) * 0.1
        
        # Consonant clusters
        complexity += len(clusters) * 0.15
        
        # Special complexity for laryngealized vowels
        if VocalType.LARYNGEALIZED in vocal_types:
            complexity += 0.2
        
        return min(complexity, 1.0)
    
    def generate_ipa_transcription(self, shuar_word: str) -> str:
        """Generate IPA transcription for a Shuar word."""
        if not shuar_word:
            return ""
        
        word = shuar_word.lower().strip()
        ipa_transcription = ""
        i = 0
        
        while i < len(word):
            # Check for digraphs first
            if i < len(word) - 1:
                digraph = word[i:i+2]
                if digraph in self.DIGRAPHS:
                    ipa_transcription += self.IPA_MAPPINGS.get(digraph, digraph)
                    i += 2
                    continue
            
            # Single character
            char = word[i]
            ipa_transcription += self.IPA_MAPPINGS.get(char, char)
            i += 1
        
        return ipa_transcription
    
    def create_phonological_info(self, shuar_word: str) -> PhonologicalInfo:
        """Create PhonologicalInfo entity from analysis."""
        features = self.analyze_word(shuar_word)
        ipa_transcription = self.generate_ipa_transcription(shuar_word)
        
        return PhonologicalInfo(
            ipa_transcription=ipa_transcription,
            has_nasal_vowels=VocalType.NASAL in features.vocal_types,
            has_laryngealized_vowels=VocalType.LARYNGEALIZED in features.vocal_types,
            vocal_types_present=list(features.vocal_types),
            number_of_syllables=features.syllable_count,
            syllable_pattern=features.syllable_pattern
        )
    
    def calculate_phonological_similarity(
        self, 
        word1: str, 
        word2: str
    ) -> float:
        """Calculate phonological similarity between two Shuar words."""
        if not word1 or not word2:
            return 0.0
        
        features1 = self.analyze_word(word1)
        features2 = self.analyze_word(word2)
        
        similarity_score = 0.0
        
        # Vocal type similarity (30%)
        vocal_similarity = self._calculate_vocal_type_similarity(
            features1.vocal_types, features2.vocal_types
        )
        similarity_score += vocal_similarity * 0.3
        
        # Syllable count similarity (20%)
        syllable_similarity = self._calculate_syllable_similarity(
            features1.syllable_count, features2.syllable_count
        )
        similarity_score += syllable_similarity * 0.2
        
        # Pattern similarity (25%)
        pattern_similarity = self._calculate_pattern_similarity(
            features1.syllable_pattern, features2.syllable_pattern
        )
        similarity_score += pattern_similarity * 0.25
        
        # Sound similarity (25%)
        sound_similarity = self._calculate_sound_similarity(word1, word2)
        similarity_score += sound_similarity * 0.25
        
        return min(similarity_score, 1.0)
    
    def _calculate_vocal_type_similarity(
        self, 
        types1: Set[VocalType], 
        types2: Set[VocalType]
    ) -> float:
        """Calculate similarity based on vocal types present."""
        if not types1 and not types2:
            return 1.0
        
        intersection = types1 & types2
        union = types1 | types2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_syllable_similarity(self, count1: int, count2: int) -> float:
        """Calculate similarity based on syllable count."""
        if count1 == count2:
            return 1.0
        
        diff = abs(count1 - count2)
        max_count = max(count1, count2)
        
        return max(0.0, 1.0 - (diff / max_count))
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity based on syllable patterns."""
        if pattern1 == pattern2:
            return 1.0
        
        if not pattern1 or not pattern2:
            return 0.0
        
        # Use Levenshtein distance for pattern similarity
        return self._levenshtein_similarity(pattern1, pattern2)
    
    def _calculate_sound_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity based on actual sounds."""
        ipa1 = self.generate_ipa_transcription(word1)
        ipa2 = self.generate_ipa_transcription(word2)
        
        return self._levenshtein_similarity(ipa1, ipa2)
    
    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity using Levenshtein distance."""
        if s1 == s2:
            return 1.0
        
        if not s1 or not s2:
            return 0.0
        
        # Calculate Levenshtein distance
        len1, len2 = len(s1), len(s2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        
        return 1.0 - (distance / max_len) if max_len > 0 else 0.0