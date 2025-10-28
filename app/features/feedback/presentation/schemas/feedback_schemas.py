"""Feedback API schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class FeedbackSubmissionSchema(BaseModel):
    """Schema for feedback submission."""
    translation_id: UUID
    user_id: Optional[UUID] = None
    user_role: str = Field("visitor", description="User role")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")
    suggested_translation: Optional[str] = Field(None, max_length=500, description="Suggested alternative translation")
    cultural_context: Optional[str] = Field(None, max_length=1000, description="Cultural context notes")
    pronunciation_notes: Optional[str] = Field(None, max_length=500, description="Pronunciation notes")
    is_from_native_speaker: bool = Field(False, description="Is feedback from native Shuar speaker")


class FeedbackResponseSchema(BaseModel):
    """Schema for feedback response."""
    id: UUID
    translation_id: UUID
    user_role: str
    feedback_type: str
    rating: Optional[int] = None
    comment: Optional[str] = None
    suggested_translation: Optional[str] = None
    status: str
    created_at: datetime


class TranslationFeedbackResponseSchema(BaseModel):
    """Schema for translation feedback response."""
    translation_id: UUID
    feedback: List[Dict[str, Any]]
    total_count: int
    summary: Dict[str, Any]