"""Value object representing phonological similarity between words."""

from dataclasses import dataclass
from typing import Dict, Any

from app.core.shared.exceptions import ValidationError


@dataclass(frozen=True)
class SimilarityScore:
    """Value object representing similarity between two Shuar words."""
    
    phonological_similarity: float
    morphological_similarity: float
    semantic_similarity: float
    overall_similarity: float
    
    def __post_init__(self):
        """Validate similarity scores after initialization."""
        scores = [
            self.phonological_similarity,
            self.morphological_similarity,
            self.semantic_similarity,
            self.overall_similarity
        ]
        
        for score in scores:
            if not 0.0 <= score <= 1.0:
                raise ValidationError("All similarity scores must be between 0.0 and 1.0")
        
        # Validate that overall similarity is reasonable given component scores
        expected_overall = (
            self.phonological_similarity * 0.4 +
            self.morphological_similarity * 0.3 +
            self.semantic_similarity * 0.3
        )
        
        if abs(self.overall_similarity - expected_overall) > 0.1:
            raise ValidationError("Overall similarity score is inconsistent with component scores")
    
    @classmethod
    def create(cls, phonological: float, morphological: float, semantic: float) -> 'SimilarityScore':
        """Create a similarity score with calculated overall score."""
        overall = phonological * 0.4 + morphological * 0.3 + semantic * 0.3
        
        return cls(
            phonological_similarity=phonological,
            morphological_similarity=morphological,
            semantic_similarity=semantic,
            overall_similarity=overall
        )
    
    def is_high_similarity(self) -> bool:
        """Check if this represents high similarity (>= 0.7)."""
        return self.overall_similarity >= 0.7
    
    def is_moderate_similarity(self) -> bool:
        """Check if this represents moderate similarity (0.4 - 0.7)."""
        return 0.4 <= self.overall_similarity < 0.7
    
    def is_low_similarity(self) -> bool:
        """Check if this represents low similarity (< 0.4)."""
        return self.overall_similarity < 0.4
    
    def get_similarity_level(self) -> str:
        """Get similarity level as string."""
        if self.is_high_similarity():
            return "high"
        elif self.is_moderate_similarity():
            return "moderate"
        else:
            return "low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "phonological_similarity": self.phonological_similarity,
            "morphological_similarity": self.morphological_similarity,
            "semantic_similarity": self.semantic_similarity,
            "overall_similarity": self.overall_similarity,
            "similarity_level": self.get_similarity_level()
        }