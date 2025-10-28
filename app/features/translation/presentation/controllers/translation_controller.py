"""Translation API controller."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from app.features.translation.application.use_cases.translate_text_use_case import (
    TranslateTextUseCase, TranslateTextRequest
)
from app.features.translation.application.use_cases.find_similar_words_use_case import (
    FindSimilarWordsUseCase, FindSimilarWordsRequest
)
from app.features.translation.application.use_cases.get_translation_with_phonetics_use_case import (
    GetTranslationWithPhoneticsUseCase, GetTranslationWithPhoneticsRequest
)
from app.features.translation.presentation.schemas.translation_schemas import (
    TranslationRequestSchema, TranslationResponseSchema,
    SimilarWordsRequestSchema, SimilarWordsResponseSchema,
    DetailedTranslationRequestSchema, DetailedTranslationResponseSchema
)
from app.core.shared.container import container

router = APIRouter()


@router.post("/translate", response_model=TranslationResponseSchema)
async def translate_text(
    request: TranslationRequestSchema,
    translate_use_case: TranslateTextUseCase = Depends(lambda: container.translate_text_use_case())
):
    """Translate text between Shuar and Spanish."""
    try:
        use_case_request = TranslateTextRequest(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            include_phonetics=request.include_phonetics,
            include_morphology=request.include_morphology,
            include_similar_words=request.include_similar_words,
            max_similar_words=request.max_similar_words
        )
        
        result = await translate_use_case.execute(use_case_request)
        
        return TranslationResponseSchema(
            original_text=result.original_text,
            detected_language=result.detected_language,
            translations=result.translations,
            phonetic_info=result.phonetic_info,
            morphological_analysis=result.morphological_analysis,
            similar_words=[sw.to_dict() for sw in result.similar_words],
            confidence_score=result.confidence_score,
            processing_time_ms=result.processing_time_ms,
            word_count=result.word_count,
            has_exact_translation=result.has_exact_translation(),
            has_similar_words=result.has_similar_words(),
            is_high_quality=result.is_high_quality()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/similar/{word}", response_model=SimilarWordsResponseSchema)
async def find_similar_words(
    word: str,
    language: str = "shuar",
    similarity_threshold: float = 0.3,
    max_results: int = 10,
    include_morphological: bool = True,
    similar_words_use_case: FindSimilarWordsUseCase = Depends(lambda: container.find_similar_words_use_case())
):
    """Find words similar to the given word."""
    try:
        use_case_request = FindSimilarWordsRequest(
            word=word,
            language=language,
            similarity_threshold=similarity_threshold,
            max_results=max_results,
            include_morphological=include_morphological
        )
        
        similar_words = await similar_words_use_case.execute(use_case_request)
        
        return SimilarWordsResponseSchema(
            query_word=word,
            language=language,
            similar_words=[sw.to_dict() for sw in similar_words],
            total_found=len(similar_words)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/detailed/{word}", response_model=DetailedTranslationResponseSchema)
async def get_detailed_translation(
    word: str,
    source_language: str = "shuar",
    include_alternatives: bool = True,
    include_usage_examples: bool = True,
    include_cultural_notes: bool = True,
    detailed_translation_use_case: GetTranslationWithPhoneticsUseCase = Depends(lambda: container.get_translation_with_phonetics_use_case())
):
    """Get detailed translation information with phonetics and morphology."""
    try:
        use_case_request = GetTranslationWithPhoneticsRequest(
            word=word,
            source_language=source_language,
            include_alternatives=include_alternatives,
            include_usage_examples=include_usage_examples,
            include_cultural_notes=include_cultural_notes,
            include_quality_metrics=True
        )
        
        result = await detailed_translation_use_case.execute(use_case_request)
        
        return DetailedTranslationResponseSchema(
            source_word=result.source_word,
            primary_translation=result.primary_translation,
            alternative_translations=result.alternative_translations,
            phonetic_analysis=result.phonetic_analysis,
            morphological_analysis=result.morphological_analysis,
            usage_examples=result.usage_examples,
            cultural_notes=result.cultural_notes,
            quality_metrics=result.quality_metrics,
            related_words=result.related_words
        )
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))