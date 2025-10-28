"""Dependency injection container configuration."""

from dependency_injector import containers, providers

from app.core.shared.config import settings
from app.core.infrastructure.supabase_client import SupabaseClient

# Domain services
from app.features.translation.domain.services.phonological_analysis_service import PhonologicalAnalysisService
from app.features.translation.domain.services.language_detection_service import LanguageDetectionService
from app.features.translation.domain.services.translation_scoring_service import TranslationScoringService
from app.features.translation.domain.services.similarity_search_service import SimilaritySearchService

# Repositories
from app.features.translation.infrastructure.repositories.supabase_word_repository import SupabaseWordRepository
from app.features.translation.infrastructure.repositories.supabase_translation_repository import SupabaseTranslationRepository
from app.features.feedback.infrastructure.repositories.supabase_feedback_repository import SupabaseFeedbackRepository

# Use cases
from app.features.translation.application.use_cases.translate_text_use_case import TranslateTextUseCase
from app.features.translation.application.use_cases.find_similar_words_use_case import FindSimilarWordsUseCase
from app.features.translation.application.use_cases.get_translation_with_phonetics_use_case import GetTranslationWithPhoneticsUseCase
from app.features.feedback.application.use_cases.submit_feedback_use_case import SubmitFeedbackUseCase, GetTranslationFeedbackUseCase
from app.features.admin.application.use_cases.add_new_word_use_case import AddNewWordUseCase
from app.features.admin.application.use_cases.review_feedback_use_case import ReviewFeedbackUseCase, GetPendingFeedbackUseCase


class Container(containers.DeclarativeContainer):
    """IoC container for dependency injection."""
    
    # Configuration
    config = providers.Configuration()
    
    # External services
    supabase_client = providers.Singleton(
        SupabaseClient,
        url=settings.supabase_url,
        key=settings.supabase_anon_key,
        service_role_key=settings.supabase_service_role_key
    )
    
    # Repositories
    word_repository = providers.Factory(
        SupabaseWordRepository,
        supabase_client=supabase_client
    )
    
    translation_repository = providers.Factory(
        SupabaseTranslationRepository,
        supabase_client=supabase_client
    )
    
    feedback_repository = providers.Factory(
        SupabaseFeedbackRepository,
        supabase_client=supabase_client
    )
    
    # Domain services
    phonological_service = providers.Factory(PhonologicalAnalysisService)
    
    language_detection_service = providers.Factory(LanguageDetectionService)
    
    translation_scoring_service = providers.Factory(TranslationScoringService)
    
    similarity_search_service = providers.Factory(
        SimilaritySearchService,
        phonological_service=phonological_service
    )
    
    # Use cases
    translate_text_use_case = providers.Factory(
        TranslateTextUseCase,
        word_repository=word_repository,
        translation_repository=translation_repository,
        language_detection_service=language_detection_service,
        phonological_service=phonological_service,
        similarity_service=similarity_search_service
    )
    
    find_similar_words_use_case = providers.Factory(
        FindSimilarWordsUseCase,
        word_repository=word_repository,
        similarity_service=similarity_search_service,
        phonological_service=phonological_service
    )
    
    get_translation_with_phonetics_use_case = providers.Factory(
        GetTranslationWithPhoneticsUseCase,
        word_repository=word_repository,
        translation_repository=translation_repository,
        feedback_repository=feedback_repository,
        phonological_service=phonological_service,
        scoring_service=translation_scoring_service
    )
    
    submit_feedback_use_case = providers.Factory(
        SubmitFeedbackUseCase,
        feedback_repository=feedback_repository,
        translation_repository=translation_repository
    )
    
    get_translation_feedback_use_case = providers.Factory(
        GetTranslationFeedbackUseCase,
        feedback_repository=feedback_repository
    )
    
    add_new_word_use_case = providers.Factory(
        AddNewWordUseCase,
        word_repository=word_repository,
        phonological_service=phonological_service
    )
    
    review_feedback_use_case = providers.Factory(
        ReviewFeedbackUseCase,
        feedback_repository=feedback_repository,
        translation_repository=translation_repository
    )
    
    get_pending_feedback_use_case = providers.Factory(
        GetPendingFeedbackUseCase,
        feedback_repository=feedback_repository
    )


# Global container instance
container = Container()