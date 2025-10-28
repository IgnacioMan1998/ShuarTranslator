"""Admin API schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class AddWordRequestSchema(BaseModel):
    """Schema for adding new word."""
    shuar_text: str = Field(..., min_length=1, max_length=100)
    spanish_translation: str = Field(..., min_length=1, max_length=100)
    word_type: Optional[str] = Field(None, description="Word type (noun, verb, etc.)")
    definition_extended: Optional[str] = Field(None, max_length=2000)
    ipa_transcription: Optional[str] = Field(None, max_length=100)
    vocal_types: Optional[List[str]] = Field(None, description="Vocal types present")
    root_word: Optional[str] = Field(None, max_length=50)
    is_compound: bool = Field(False)
    compound_components: Optional[List[str]] = Field(None)
    applied_suffixes: Optional[List[str]] = Field(None)
    usage_examples: Optional[List[Dict[str, str]]] = Field(None)
    synonyms: Optional[List[str]] = Field(None)
    antonyms: Optional[List[str]] = Field(None)
    cultural_notes: Optional[str] = Field(None, max_length=1000)
    confidence_level: float = Field(0.8, ge=0.0, le=1.0)
    is_verified: bool = Field(True)


class WordResponseSchema(BaseModel):
    """Schema for word response."""
    id: UUID
    shuar_text: str
    spanish_translation: str
    word_type: Optional[str] = None
    confidence_level: float
    is_verified: bool
    created_at: datetime


class ReviewFeedbackRequestSchema(BaseModel):
    """Schema for reviewing feedback."""
    expert_id: UUID
    action: str = Field(..., description="Action: approve, reject, implement")
    expert_notes: Optional[str] = Field(None, max_length=1000)


class PendingFeedbackResponseSchema(BaseModel):
    """Schema for pending feedback response."""
    feedback: List[Dict[str, Any]]
    total_count: int
    high_priority_count: int
    native_speaker_count: int