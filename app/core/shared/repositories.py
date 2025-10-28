"""Central import point for all repository interfaces."""

# Base repository interfaces
from app.core.shared.repository_base import (
    IBaseRepository,
    ISearchableRepository,
    IAnalyticsRepository,
    IUnitOfWork
)

# Translation feature repositories
from app.features.translation.domain.repositories.word_repository import IWordRepository
from app.features.translation.domain.repositories.translation_repository import ITranslationRepository
from app.features.translation.domain.repositories.phonological_repository import IPhonologicalRepository

# Feedback feature repositories
from app.features.feedback.domain.repositories.feedback_repository import IFeedbackRepository

# Admin feature repositories
from app.features.admin.domain.repositories.user_repository import IUserRepository

__all__ = [
    # Base interfaces
    'IBaseRepository',
    'ISearchableRepository', 
    'IAnalyticsRepository',
    'IUnitOfWork',
    
    # Feature repositories
    'IWordRepository',
    'ITranslationRepository',
    'IPhonologicalRepository',
    'IFeedbackRepository',
    'IUserRepository'
]