"""Feedback application use cases."""

from app.features.feedback.application.use_cases.submit_feedback_use_case import (
    SubmitFeedbackUseCase,
    SubmitFeedbackRequest,
    GetTranslationFeedbackUseCase,
    GetTranslationFeedbackRequest,
    SuggestAlternativeTranslationUseCase,
    SuggestAlternativeTranslationRequest
)

__all__ = [
    'SubmitFeedbackUseCase',
    'SubmitFeedbackRequest',
    'GetTranslationFeedbackUseCase', 
    'GetTranslationFeedbackRequest',
    'SuggestAlternativeTranslationUseCase',
    'SuggestAlternativeTranslationRequest'
]