"""Translation API schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class TranslationRequestSchema(BaseModel):
    """Schema for translation request."""
    text: str = Field(..., min_length=1, max_length=500, description="Text to translate")
    source_language: Optional[str] = Field(None, description="Source language (shuar, spanish, or auto)")
    target_language: str = Field("auto", description="Target language (shuar, spanish, or auto)")
    include_phonetics: bool = Field(True, description="Include phonetic information")
    include_morphology: bool = Field(True, description="Include morphological analysis")
    include_similar_words: bool = Field(True, description="Include similar word suggestions")
    max_similar_words: int = Field(5, ge=1, le=20, description="Maximum number of similar words")


class TranslationResponseSchema(BaseModel):
    """Schema for translation response."""
    original_text: str
    detected_language: str
    translations: List[Dict[str, Any]]
    phonetic_info: Optional[Dict[str, Any]] = None
    morphological_analysis: Optional[Dict[str, Any]] = None
    similar_words: List[Dict[str, Any]] = []
    confidence_score: float
    processing_time_ms: int
    word_count: int
    has_exact_translation: bool
    has_similar_words: bool
    is_high_quality: bool


class SimilarWordsRequestSchema(BaseModel):
    """Schema for similar words request."""
    word: str = Field(..., min_length=1, max_length=100)
    language: str = Field("shuar", description="Language of the word")
    similarity_threshold: float = Field(0.3, ge=0.0, le=1.0)
    max_results: int = Field(10, ge=1, le=50)
    include_morphological: bool = Field(True)


class SimilarWordsResponseSchema(BaseModel):
    """Schema for similar words response."""
    query_word: str
    language: str
    similar_words: List[Dict[str, Any]]
    total_found: int


class DetailedTranslationRequestSchema(BaseModel):
    """Schema for detailed translation request."""
    word: str = Field(..., min_length=1, max_length=100)
    source_language: str = Field("shuar", description="Source language")
    include_alternatives: bool = Field(True)
    include_usage_examples: bool = Field(True)
    include_cultural_notes: bool = Field(True)


class DetailedTranslationResponseSchema(BaseModel):
    """Schema for detailed translation response."""
    source_word: Dict[str, Any]
    primary_translation: Dict[str, Any]
    alternative_translations: List[Dict[str, Any]]
    phonetic_analysis: Optional[Dict[str, Any]] = None
    morphological_analysis: Optional[Dict[str, Any]] = None
    usage_examples: List[Dict[str, Any]]
    cultural_notes: Optional[str] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    related_words: List[Dict[str, Any]]