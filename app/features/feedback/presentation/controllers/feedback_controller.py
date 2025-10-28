"""Feedback API controller."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID

from app.features.feedback.application.use_cases.submit_feedback_use_case import (
    SubmitFeedbackUseCase, SubmitFeedbackRequest,
    GetTranslationFeedbackUseCase, GetTranslationFeedbackRequest
)
from app.features.feedback.presentation.schemas.feedback_schemas import (
    FeedbackSubmissionSchema, FeedbackResponseSchema,
    TranslationFeedbackResponseSchema
)
from app.core.shared.container import container

router = APIRouter()


@router.post("/submit", response_model=FeedbackResponseSchema)
async def submit_feedback(
    request: FeedbackSubmissionSchema,
    submit_feedback_use_case: SubmitFeedbackUseCase = Depends(lambda: container.submit_feedback_use_case())
):
    """Submit feedback on a translation."""
    try:
        use_case_request = SubmitFeedbackRequest(
            translation_id=request.translation_id,
            user_id=request.user_id,
            user_role=request.user_role,
            rating=request.rating,
            comment=request.comment,
            suggested_translation=request.suggested_translation,
            cultural_context=request.cultural_context,
            pronunciation_notes=request.pronunciation_notes,
            is_from_native_speaker=request.is_from_native_speaker
        )
        
        feedback = await submit_feedback_use_case.execute(use_case_request)
        
        return FeedbackResponseSchema(
            id=feedback.id,
            translation_id=feedback.translation_id,
            user_role=feedback.user_role.value,
            feedback_type=feedback.feedback_type.value,
            rating=feedback.rating,
            comment=feedback.comment,
            suggested_translation=feedback.suggested_translation,
            status=feedback.status.value,
            created_at=feedback.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/translation/{translation_id}", response_model=TranslationFeedbackResponseSchema)
async def get_translation_feedback(
    translation_id: UUID,
    include_pending: bool = True,
    include_rejected: bool = False,
    limit: int = 50,
    offset: int = 0,
    get_feedback_use_case: GetTranslationFeedbackUseCase = Depends(lambda: container.get_translation_feedback_use_case())
):
    """Get feedback for a specific translation."""
    try:
        use_case_request = GetTranslationFeedbackRequest(
            translation_id=translation_id,
            include_pending=include_pending,
            include_rejected=include_rejected,
            limit=limit,
            offset=offset
        )
        
        result = await get_feedback_use_case.execute(use_case_request)
        
        return TranslationFeedbackResponseSchema(
            translation_id=translation_id,
            feedback=result["feedback"],
            total_count=result["total_count"],
            summary=result["summary"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))