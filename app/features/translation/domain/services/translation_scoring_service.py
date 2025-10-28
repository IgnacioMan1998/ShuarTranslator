"""Translation scoring service for calculating translation confidence and quality."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.features.translation.domain.entities.translation import Translation
from app.features.translation.domain.entities.word import Word
from app.features.feedback.domain.entities.feedback import Feedback, UserRole
from app.features.translation.domain.value_objects.similarity_score import SimilarityScore


@dataclass
class TranslationQualityMetrics:
    """Metrics for evaluating translation quality."""
    confidence_score: float
    community_rating: float
    expert_approval: bool
    usage_frequency: int
    feedback_count: int
    native_speaker_approval: bool
    phonological_accuracy: float
    cultural_appropriateness: float
    overall_quality_score: float


class TranslationScoringService:
    """Domain service for scoring and evaluating translation quality."""
    
    # Weights for different quality factors
    COMMUNITY_RATING_WEIGHT = 0.25
    EXPERT_APPROVAL_WEIGHT = 0.30
    USAGE_FREQUENCY_WEIGHT = 0.15
    PHONOLOGICAL_ACCURACY_WEIGHT = 0.15
    CULTURAL_APPROPRIATENESS_WEIGHT = 0.15
    
    # Role-based feedback weights
    FEEDBACK_WEIGHTS = {
        UserRole.VISITOR: 1.0,
        UserRole.COMMUNITY_MEMBER: 1.2,
        UserRole.VERIFIED_SPEAKER: 2.0,
        UserRole.EXPERT: 3.0,
        UserRole.ADMIN: 3.0
    }
    
    def calculate_translation_confidence(
        self, 
        translation: Translation,
        source_word: Optional[Word] = None,
        feedback_list: Optional[List[Feedback]] = None
    ) -> float:
        """Calculate confidence score for a translation."""
        confidence_factors = []
        
        # Base confidence from translation status
        status_confidence = self._get_status_confidence(translation)
        confidence_factors.append(('status', status_confidence, 0.3))
        
        # Community rating confidence
        if translation.total_ratings > 0:
            rating_confidence = self._calculate_rating_confidence(
                translation.average_rating, translation.total_ratings
            )
            confidence_factors.append(('rating', rating_confidence, 0.25))
        
        # Usage frequency confidence
        usage_confidence = self._calculate_usage_confidence(translation.usage_count)
        confidence_factors.append(('usage', usage_confidence, 0.15))
        
        # Word-based confidence (if source word available)
        if source_word:
            word_confidence = self._calculate_word_based_confidence(source_word)
            confidence_factors.append(('word', word_confidence, 0.15))
        
        # Feedback-based confidence
        if feedback_list:
            feedback_confidence = self._calculate_feedback_confidence(feedback_list)
            confidence_factors.append(('feedback', feedback_confidence, 0.15))
        
        # Calculate weighted average
        total_weight = sum(weight for _, _, weight in confidence_factors)
        if total_weight == 0:
            return 0.5  # Default confidence
        
        weighted_sum = sum(score * weight for _, score, weight in confidence_factors)
        return min(1.0, weighted_sum / total_weight)
    
    def calculate_quality_metrics(
        self,
        translation: Translation,
        feedback_list: List[Feedback],
        source_word: Optional[Word] = None
    ) -> TranslationQualityMetrics:
        """Calculate comprehensive quality metrics for a translation."""
        
        # Basic metrics
        confidence_score = self.calculate_translation_confidence(
            translation, source_word, feedback_list
        )
        
        # Community rating (weighted by user roles)
        community_rating = self._calculate_weighted_community_rating(feedback_list)
        
        # Expert approval
        expert_approval = translation.approved_by is not None
        
        # Usage metrics
        usage_frequency = translation.usage_count
        feedback_count = len(feedback_list)
        
        # Native speaker approval
        native_speaker_approval = self._has_native_speaker_approval(feedback_list)
        
        # Phonological accuracy (if source word available)
        phonological_accuracy = 0.5  # Default
        if source_word and source_word.phonological_info:
            phonological_accuracy = self._assess_phonological_accuracy(
                translation, source_word
            )
        
        # Cultural appropriateness
        cultural_appropriateness = self._assess_cultural_appropriateness(
            translation, feedback_list
        )
        
        # Overall quality score
        overall_quality_score = self._calculate_overall_quality(
            confidence_score,
            community_rating,
            expert_approval,
            usage_frequency,
            phonological_accuracy,
            cultural_appropriateness
        )
        
        return TranslationQualityMetrics(
            confidence_score=confidence_score,
            community_rating=community_rating,
            expert_approval=expert_approval,
            usage_frequency=usage_frequency,
            feedback_count=feedback_count,
            native_speaker_approval=native_speaker_approval,
            phonological_accuracy=phonological_accuracy,
            cultural_appropriateness=cultural_appropriateness,
            overall_quality_score=overall_quality_score
        )
    
    def _get_status_confidence(self, translation: Translation) -> float:
        """Get confidence based on translation status."""
        from app.features.translation.domain.entities.translation import TranslationStatus
        
        status_scores = {
            TranslationStatus.APPROVED: 0.9,
            TranslationStatus.NEEDS_REVIEW: 0.6,
            TranslationStatus.PENDING: 0.4,
            TranslationStatus.REJECTED: 0.1
        }
        
        return status_scores.get(translation.status, 0.5)
    
    def _calculate_rating_confidence(self, average_rating: float, total_ratings: int) -> float:
        """Calculate confidence based on community ratings."""
        if total_ratings == 0:
            return 0.5
        
        # Base confidence from rating (1-5 scale to 0-1 scale)
        rating_confidence = (average_rating - 1) / 4
        
        # Adjust for number of ratings (more ratings = more reliable)
        reliability_factor = min(1.0, total_ratings / 10)  # Full reliability at 10+ ratings
        
        return rating_confidence * reliability_factor + 0.5 * (1 - reliability_factor)
    
    def _calculate_usage_confidence(self, usage_count: int) -> float:
        """Calculate confidence based on usage frequency."""
        if usage_count == 0:
            return 0.3
        
        # Logarithmic scaling for usage confidence
        import math
        return min(1.0, 0.3 + 0.7 * (math.log(usage_count + 1) / math.log(101)))
    
    def _calculate_word_based_confidence(self, word: Word) -> float:
        """Calculate confidence based on source word quality."""
        confidence = 0.5  # Base confidence
        
        # Verified words are more reliable
        if word.is_verified:
            confidence += 0.3
        
        # Higher confidence words contribute more
        confidence += word.confidence_level * 0.2
        
        # Frequently used words are more reliable
        if word.frequency_score > 10:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _calculate_feedback_confidence(self, feedback_list: List[Feedback]) -> float:
        """Calculate confidence based on feedback quality."""
        if not feedback_list:
            return 0.5
        
        weighted_scores = []
        total_weight = 0
        
        for feedback in feedback_list:
            if feedback.rating is not None:
                weight = self.FEEDBACK_WEIGHTS.get(feedback.user_role, 1.0)
                
                # Extra weight for native speakers
                if feedback.is_from_native_speaker:
                    weight *= 1.5
                
                # Convert rating to confidence (1-5 to 0-1)
                rating_confidence = (feedback.rating - 1) / 4
                
                weighted_scores.append(rating_confidence * weight)
                total_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        return sum(weighted_scores) / total_weight
    
    def _calculate_weighted_community_rating(self, feedback_list: List[Feedback]) -> float:
        """Calculate weighted average community rating."""
        if not feedback_list:
            return 0.0
        
        weighted_ratings = []
        total_weight = 0
        
        for feedback in feedback_list:
            if feedback.rating is not None:
                weight = self.FEEDBACK_WEIGHTS.get(feedback.user_role, 1.0)
                
                if feedback.is_from_native_speaker:
                    weight *= 1.5
                
                weighted_ratings.append(feedback.rating * weight)
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return sum(weighted_ratings) / total_weight
    
    def _has_native_speaker_approval(self, feedback_list: List[Feedback]) -> bool:
        """Check if translation has approval from native speakers."""
        for feedback in feedback_list:
            if (feedback.is_from_native_speaker and 
                feedback.rating is not None and 
                feedback.rating >= 4):
                return True
        return False
    
    def _assess_phonological_accuracy(
        self, 
        translation: Translation, 
        source_word: Word
    ) -> float:
        """Assess phonological accuracy of translation."""
        # This is a simplified assessment
        # In a real implementation, this would involve more sophisticated analysis
        
        accuracy = 0.5  # Base accuracy
        
        # If source word has phonological info, we can make better assessment
        if source_word.phonological_info:
            # Check if translation preserves phonological complexity
            source_complexity = len(source_word.phonological_info.vocal_types_present)
            
            # Simple heuristic: longer words might preserve more phonological info
            if len(translation.target_text) >= len(translation.source_text):
                accuracy += 0.2
            
            # Bonus for verified words
            if source_word.is_verified:
                accuracy += 0.3
        
        return min(1.0, accuracy)
    
    def _assess_cultural_appropriateness(
        self, 
        translation: Translation, 
        feedback_list: List[Feedback]
    ) -> float:
        """Assess cultural appropriateness of translation."""
        appropriateness = 0.5  # Base appropriateness
        
        # Check for cultural feedback
        cultural_feedback = [
            f for f in feedback_list 
            if f.cultural_context is not None and f.cultural_context.strip()
        ]
        
        if cultural_feedback:
            # If there's cultural feedback, assess based on ratings
            cultural_ratings = [
                f.rating for f in cultural_feedback 
                if f.rating is not None
            ]
            
            if cultural_ratings:
                avg_cultural_rating = sum(cultural_ratings) / len(cultural_ratings)
                appropriateness = (avg_cultural_rating - 1) / 4
        
        # Bonus for having cultural context in translation
        if translation.context and translation.context.cultural_notes:
            appropriateness += 0.2
        
        return min(1.0, appropriateness)
    
    def _calculate_overall_quality(
        self,
        confidence_score: float,
        community_rating: float,
        expert_approval: bool,
        usage_frequency: int,
        phonological_accuracy: float,
        cultural_appropriateness: float
    ) -> float:
        """Calculate overall quality score."""
        
        # Normalize community rating to 0-1 scale
        normalized_rating = (community_rating - 1) / 4 if community_rating > 0 else 0.5
        
        # Expert approval bonus
        expert_bonus = 0.2 if expert_approval else 0.0
        
        # Usage frequency factor (logarithmic)
        import math
        usage_factor = min(0.2, math.log(usage_frequency + 1) / 25)
        
        # Calculate weighted score
        quality_score = (
            confidence_score * self.COMMUNITY_RATING_WEIGHT +
            normalized_rating * self.EXPERT_APPROVAL_WEIGHT +
            phonological_accuracy * self.PHONOLOGICAL_ACCURACY_WEIGHT +
            cultural_appropriateness * self.CULTURAL_APPROPRIATENESS_WEIGHT +
            expert_bonus +
            usage_factor
        )
        
        return min(1.0, quality_score)
    
    def recommend_translation_improvements(
        self, 
        translation: Translation,
        quality_metrics: TranslationQualityMetrics,
        feedback_list: List[Feedback]
    ) -> List[str]:
        """Recommend improvements for a translation."""
        recommendations = []
        
        # Low confidence recommendations
        if quality_metrics.confidence_score < 0.6:
            recommendations.append("Consider seeking expert review to improve confidence")
        
        # Low community rating recommendations
        if quality_metrics.community_rating < 3.0:
            recommendations.append("Review community feedback for suggested improvements")
        
        # No expert approval
        if not quality_metrics.expert_approval:
            recommendations.append("Submit for expert linguistic review")
        
        # Low usage recommendations
        if quality_metrics.usage_frequency < 5:
            recommendations.append("Translation needs more community validation through usage")
        
        # Phonological accuracy recommendations
        if quality_metrics.phonological_accuracy < 0.6:
            recommendations.append("Review phonological accuracy with native speakers")
        
        # Cultural appropriateness recommendations
        if quality_metrics.cultural_appropriateness < 0.6:
            recommendations.append("Add cultural context or seek cultural validation")
        
        # Specific feedback-based recommendations
        negative_feedback = [f for f in feedback_list if f.rating and f.rating <= 2]
        if negative_feedback:
            recommendations.append("Address concerns raised in low-rating feedback")
        
        suggestions = [f for f in feedback_list if f.suggested_translation]
        if suggestions:
            recommendations.append("Consider alternative translations suggested by community")
        
        return recommendations