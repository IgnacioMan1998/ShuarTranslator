"""Admin API controller."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from uuid import UUID

from app.features.admin.application.use_cases.add_new_word_use_case import (
    AddNewWordUseCase, AddNewWordRequest
)
from app.features.admin.application.use_cases.review_feedback_use_case import (
    ReviewFeedbackUseCase, ReviewFeedbackRequest,
    GetPendingFeedbackUseCase, GetPendingFeedbackRequest
)
from app.features.admin.presentation.schemas.admin_schemas import (
    AddWordRequestSchema, WordResponseSchema,
    ReviewFeedbackRequestSchema, PendingFeedbackResponseSchema
)
from app.core.shared.container import container

router = APIRouter()


@router.post("/words", response_model=WordResponseSchema)
async def add_new_word(
    request: AddWordRequestSchema,
    add_word_use_case: AddNewWordUseCase = Depends(lambda: container.add_new_word_use_case())
):
    """Add a new word to the vocabulary database."""
    try:
        use_case_request = AddNewWordRequest(
            shuar_text=request.shuar_text,
            spanish_translation=request.spanish_translation,
            word_type=request.word_type,
            definition_extended=request.definition_extended,
            ipa_transcription=request.ipa_transcription,
            vocal_types=request.vocal_types,
            root_word=request.root_word,
            is_compound=request.is_compound,
            compound_components=request.compound_components,
            applied_suffixes=request.applied_suffixes,
            usage_examples=request.usage_examples,
            synonyms=request.synonyms,
            antonyms=request.antonyms,
            cultural_notes=request.cultural_notes,
            confidence_level=request.confidence_level,
            is_verified=request.is_verified
        )
        
        word = await add_word_use_case.execute(use_case_request)
        
        return WordResponseSchema(
            id=word.id,
            shuar_text=word.shuar_text,
            spanish_translation=word.spanish_translation,
            word_type=word.word_type.value if word.word_type else None,
            confidence_level=word.confidence_level,
            is_verified=word.is_verified,
            created_at=word.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pending-feedback", response_model=PendingFeedbackResponseSchema)
async def get_pending_feedback(
    expert_id: UUID,
    priority_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    get_pending_use_case: GetPendingFeedbackUseCase = Depends(lambda: container.get_pending_feedback_use_case())
):
    """Get feedback pending expert review."""
    try:
        use_case_request = GetPendingFeedbackRequest(
            expert_id=expert_id,
            priority_only=priority_only,
            limit=limit,
            offset=offset
        )
        
        result = await get_pending_use_case.execute(use_case_request)
        
        return PendingFeedbackResponseSchema(
            feedback=result["feedback"],
            total_count=result["total_count"],
            high_priority_count=result["high_priority_count"],
            native_speaker_count=result["native_speaker_count"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/feedback/{feedback_id}/review")
async def review_feedback(
    feedback_id: UUID,
    request: ReviewFeedbackRequestSchema,
    review_use_case: ReviewFeedbackUseCase = Depends(lambda: container.review_feedback_use_case())
):
    """Review and approve/reject feedback."""
    try:
        use_case_request = ReviewFeedbackRequest(
            feedback_id=feedback_id,
            expert_id=request.expert_id,
            action=request.action,
            expert_notes=request.expert_notes
        )
        
        feedback = await review_use_case.execute(use_case_request)
        
        return {
            "id": feedback.id,
            "status": feedback.status.value,
            "reviewed_by": feedback.reviewed_by,
            "reviewed_at": feedback.reviewed_at,
            "expert_notes": feedback.expert_notes
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))