"""Language detection service for identifying Shuar vs Spanish text."""

from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass
from enum import Enum

from app.features.translation.domain.entities.translation import Language
from app.core.shared.exceptions import ValidationError


class DetectionConfidence(Enum):
    """Confidence levels for language detection."""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5


@dataclass
class LanguageDetectionResult:
    """Result of language detection analysis."""
    detected_language: Language
    confidence: float
    confidence_level: DetectionConfidence
    features_detected: Dict[str, float]
    explanation: str


class LanguageDetectionService:
    """Domain service for detecting whether text is Shuar or Spanish."""
    
    # Shuar-specific phonological features
    SHUAR_VOWELS = {'a', 'e', 'i', 'u', 'á', 'é', 'í', 'ú', 'ä', 'ë', 'ï', 'ü'}
    SHUAR_NASAL_VOWELS = {'á', 'é', 'í', 'ú'}
    SHUAR_LARYNGEALIZED_VOWELS = {'ä', 'ë', 'ï', 'ü'}
    SHUAR_DIGRAPHS = {'ch', 'sh', 'ts'}
    SHUAR_CONSONANTS = {'p', 't', 'k', 's', 'j', 'm', 'n', 'r', 'w', 'y'}
    
    # Spanish-specific features
    SPANISH_VOWELS = {'a', 'e', 'i', 'o', 'u', 'á', 'é', 'í', 'ó', 'ú', 'ü'}
    SPANISH_CONSONANTS = {
        'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'ñ', 
        'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z'
    }
    SPANISH_DIGRAPHS = {'ch', 'll', 'rr'}
    
    # Common Shuar words and patterns
    SHUAR_COMMON_WORDS = {
        'yawa', 'jea', 'shuar', 'arutam', 'núka', 'apa', 'entsa', 
        'tsaa', 'saant', 'kunkuk', 'chichim', 'wampish', 'nuna',
        'mama', 'tau', 'inia', 'uunt', 'yä', 'takuni', 'tsáanin'
    }
    
    # Common Spanish words
    SPANISH_COMMON_WORDS = {
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 
        'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para',
        'casa', 'perro', 'agua', 'bueno', 'grande', 'persona', 'sol'
    }
    
    # Shuar morphological patterns
    SHUAR_SUFFIXES = {'-ni', '-ai', '-ka', '-ma', '-ta', '-nu', '-tu', '-chi'}
    
    # Spanish morphological patterns
    SPANISH_SUFFIXES = {'-ción', '-dad', '-mente', '-oso', '-osa', '-ado', '-ada', '-ero', '-era'}
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect the language of the input text."""
        if not text or not text.strip():
            raise ValidationError("Text cannot be empty")
        
        text = text.lower().strip()
        
        # Calculate feature scores
        features = self._analyze_features(text)
        
        # Calculate overall scores
        shuar_score = self._calculate_shuar_score(features)
        spanish_score = self._calculate_spanish_score(features)
        
        # Determine detected language and confidence
        if shuar_score > spanish_score:
            detected_language = Language.SHUAR
            confidence = shuar_score / (shuar_score + spanish_score)
        else:
            detected_language = Language.SPANISH
            confidence = spanish_score / (shuar_score + spanish_score)
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(confidence)
        
        # Generate explanation
        explanation = self._generate_explanation(
            detected_language, features, shuar_score, spanish_score
        )
        
        return LanguageDetectionResult(
            detected_language=detected_language,
            confidence=confidence,
            confidence_level=confidence_level,
            features_detected=features,
            explanation=explanation
        )
    
    def _analyze_features(self, text: str) -> Dict[str, float]:
        """Analyze linguistic features of the text."""
        words = text.split()
        total_chars = len(text.replace(' ', ''))
        
        features = {}
        
        # Phonological features
        features['shuar_nasal_vowels'] = self._count_feature_ratio(
            text, self.SHUAR_NASAL_VOWELS, total_chars
        )
        features['shuar_laryngealized_vowels'] = self._count_feature_ratio(
            text, self.SHUAR_LARYNGEALIZED_VOWELS, total_chars
        )
        features['shuar_digraphs'] = self._count_digraph_ratio(
            text, self.SHUAR_DIGRAPHS, len(words)
        )
        features['spanish_digraphs'] = self._count_digraph_ratio(
            text, self.SPANISH_DIGRAPHS, len(words)
        )
        
        # Vowel system features
        features['has_spanish_o'] = 1.0 if 'o' in text else 0.0
        features['vowel_system_shuar'] = self._analyze_vowel_system_shuar(text)
        features['vowel_system_spanish'] = self._analyze_vowel_system_spanish(text)
        
        # Lexical features
        features['shuar_common_words'] = self._count_common_words(
            words, self.SHUAR_COMMON_WORDS
        )
        features['spanish_common_words'] = self._count_common_words(
            words, self.SPANISH_COMMON_WORDS
        )
        
        # Morphological features
        features['shuar_suffixes'] = self._count_suffix_patterns(
            words, self.SHUAR_SUFFIXES
        )
        features['spanish_suffixes'] = self._count_suffix_patterns(
            words, self.SPANISH_SUFFIXES
        )
        
        # Character frequency features
        features['consonant_density'] = self._calculate_consonant_density(text)
        features['vowel_diversity'] = self._calculate_vowel_diversity(text)
        
        # Length and structure features
        features['avg_word_length'] = sum(len(word) for word in words) / len(words) if words else 0
        features['syllable_complexity'] = self._estimate_syllable_complexity(text)
        
        return features
    
    def _count_feature_ratio(self, text: str, feature_set: set, total_chars: int) -> float:
        """Count ratio of specific features in text."""
        if total_chars == 0:
            return 0.0
        
        count = sum(1 for char in text if char in feature_set)
        return count / total_chars
    
    def _count_digraph_ratio(self, text: str, digraphs: set, total_words: int) -> float:
        """Count ratio of digraphs in text."""
        if total_words == 0:
            return 0.0
        
        count = sum(text.count(digraph) for digraph in digraphs)
        return count / total_words
    
    def _analyze_vowel_system_shuar(self, text: str) -> float:
        """Analyze how well text fits Shuar vowel system."""
        vowels_found = set(char for char in text if char in self.SHUAR_VOWELS)
        
        # Shuar typically uses 4 base vowels + diacritics
        base_vowels = {'a', 'e', 'i', 'u'}
        base_found = vowels_found & base_vowels
        
        score = len(base_found) / 4.0  # Base score
        
        # Bonus for nasal/laryngealized vowels (distinctive Shuar features)
        if vowels_found & self.SHUAR_NASAL_VOWELS:
            score += 0.3
        if vowels_found & self.SHUAR_LARYNGEALIZED_VOWELS:
            score += 0.4
        
        # Penalty for Spanish 'o'
        if 'o' in vowels_found:
            score -= 0.5
        
        return max(0.0, min(1.0, score))
    
    def _analyze_vowel_system_spanish(self, text: str) -> float:
        """Analyze how well text fits Spanish vowel system."""
        vowels_found = set(char for char in text if char in self.SPANISH_VOWELS)
        
        # Spanish uses 5 vowels
        base_vowels = {'a', 'e', 'i', 'o', 'u'}
        base_found = vowels_found & base_vowels
        
        score = len(base_found) / 5.0
        
        # Bonus for having 'o' (not in Shuar)
        if 'o' in vowels_found:
            score += 0.3
        
        # Penalty for Shuar-specific diacritics
        if vowels_found & self.SHUAR_LARYNGEALIZED_VOWELS:
            score -= 0.6
        
        return max(0.0, min(1.0, score))
    
    def _count_common_words(self, words: List[str], common_set: set) -> float:
        """Count ratio of common words found."""
        if not words:
            return 0.0
        
        matches = sum(1 for word in words if word in common_set)
        return matches / len(words)
    
    def _count_suffix_patterns(self, words: List[str], suffix_set: set) -> float:
        """Count ratio of words with specific suffix patterns."""
        if not words:
            return 0.0
        
        matches = 0
        for word in words:
            for suffix in suffix_set:
                if word.endswith(suffix):
                    matches += 1
                    break
        
        return matches / len(words)
    
    def _calculate_consonant_density(self, text: str) -> float:
        """Calculate consonant density in text."""
        if not text:
            return 0.0
        
        consonants = sum(1 for char in text if char.isalpha() and char not in self.SHUAR_VOWELS)
        total_letters = sum(1 for char in text if char.isalpha())
        
        return consonants / total_letters if total_letters > 0 else 0.0
    
    def _calculate_vowel_diversity(self, text: str) -> float:
        """Calculate vowel diversity in text."""
        vowels_found = set(char for char in text if char in self.SHUAR_VOWELS | self.SPANISH_VOWELS)
        max_possible = len(self.SPANISH_VOWELS)  # Spanish has more vowels
        
        return len(vowels_found) / max_possible
    
    def _estimate_syllable_complexity(self, text: str) -> float:
        """Estimate syllable complexity (simplified)."""
        words = text.split()
        if not words:
            return 0.0
        
        total_complexity = 0
        for word in words:
            # Simple heuristic: consonant clusters increase complexity
            clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', word)
            complexity = len(clusters) / len(word) if word else 0
            total_complexity += complexity
        
        return total_complexity / len(words)
    
    def _calculate_shuar_score(self, features: Dict[str, float]) -> float:
        """Calculate overall Shuar language score."""
        score = 0.0
        
        # Strong Shuar indicators
        score += features['shuar_nasal_vowels'] * 3.0
        score += features['shuar_laryngealized_vowels'] * 4.0
        score += features['vowel_system_shuar'] * 2.0
        score += features['shuar_common_words'] * 3.0
        score += features['shuar_suffixes'] * 2.0
        
        # Shuar digraphs (shared with Spanish 'ch', but 'ts' and 'sh' are distinctive)
        score += features['shuar_digraphs'] * 1.5
        
        # Structural features that favor Shuar
        if features['avg_word_length'] > 4:  # Shuar words tend to be longer due to agglutination
            score += 1.0
        
        return score
    
    def _calculate_spanish_score(self, features: Dict[str, float]) -> float:
        """Calculate overall Spanish language score."""
        score = 0.0
        
        # Strong Spanish indicators
        score += features['has_spanish_o'] * 3.0
        score += features['vowel_system_spanish'] * 2.0
        score += features['spanish_common_words'] * 3.0
        score += features['spanish_suffixes'] * 2.0
        score += features['spanish_digraphs'] * 1.5
        
        # Penalty for Shuar-specific features
        score -= features['shuar_laryngealized_vowels'] * 2.0
        score -= features['shuar_nasal_vowels'] * 1.0
        
        return max(0.0, score)
    
    def _get_confidence_level(self, confidence: float) -> DetectionConfidence:
        """Determine confidence level based on score."""
        if confidence > 0.8:
            return DetectionConfidence.HIGH
        elif confidence > 0.5:
            return DetectionConfidence.MEDIUM
        else:
            return DetectionConfidence.LOW
    
    def _generate_explanation(
        self, 
        detected_language: Language, 
        features: Dict[str, float], 
        shuar_score: float, 
        spanish_score: float
    ) -> str:
        """Generate human-readable explanation of detection."""
        explanations = []
        
        if detected_language == Language.SHUAR:
            if features['shuar_laryngealized_vowels'] > 0:
                explanations.append("Contains laryngealized vowels (ä, ë, ï, ü) unique to Shuar")
            if features['shuar_nasal_vowels'] > 0:
                explanations.append("Contains nasal vowels (á, é, í, ú) typical of Shuar")
            if features['shuar_common_words'] > 0:
                explanations.append("Contains common Shuar words")
            if features['has_spanish_o'] == 0:
                explanations.append("Lacks the vowel 'o' which is absent in Shuar")
        else:
            if features['has_spanish_o'] > 0:
                explanations.append("Contains the vowel 'o' which is present in Spanish but not Shuar")
            if features['spanish_common_words'] > 0:
                explanations.append("Contains common Spanish words")
            if features['spanish_suffixes'] > 0:
                explanations.append("Contains Spanish morphological patterns")
        
        base_explanation = f"Detected as {detected_language.value.title()} "
        base_explanation += f"(Shuar score: {shuar_score:.2f}, Spanish score: {spanish_score:.2f})"
        
        if explanations:
            return base_explanation + ". " + "; ".join(explanations) + "."
        else:
            return base_explanation + ". Based on general linguistic patterns."