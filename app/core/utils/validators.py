"""Validation utilities for Shuar language processing."""

import re
from typing import List, Optional

from app.core.shared.exceptions import ValidationError


class ShuarTextValidator:
    """Validator for Shuar text input."""
    
    # Shuar alphabet characters including diacritics
    SHUAR_ALPHABET = {
        'a', 'á', 'ä', 'ch', 'e', 'é', 'ë', 'i', 'í', 'ï', 
        'j', 'k', 'm', 'n', 'p', 'r', 's', 'sh', 't', 'ts', 
        'u', 'ú', 'ü', 'w', 'y'
    }
    
    # Vocal types
    ORAL_VOWELS = {'a', 'e', 'i', 'u'}
    NASAL_VOWELS = {'á', 'é', 'í', 'ú'}
    LARYNGEALIZED_VOWELS = {'ä', 'ë', 'ï', 'ü'}
    
    @classmethod
    def is_valid_shuar_text(cls, text: str) -> bool:
        """Check if text contains only valid Shuar characters."""
        if not text or not text.strip():
            return False
            
        # Normalize text (lowercase, strip whitespace)
        normalized = text.lower().strip()
        
        # Check for digraphs first (ch, sh, ts)
        digraphs = ['ch', 'sh', 'ts']
        temp_text = normalized
        
        for digraph in digraphs:
            temp_text = temp_text.replace(digraph, 'X')  # Replace with placeholder
        
        # Check remaining characters
        for char in temp_text:
            if char.isspace():
                continue
            if char == 'X':  # Placeholder for digraphs
                continue
            if char not in cls.SHUAR_ALPHABET:
                return False
                
        return True
    
    @classmethod
    def validate_shuar_text(cls, text: str, max_length: int = 500) -> str:
        """Validate and normalize Shuar text input."""
        if not text:
            raise ValidationError("Text cannot be empty")
            
        if len(text) > max_length:
            raise ValidationError(f"Text exceeds maximum length of {max_length} characters")
        
        normalized = text.strip()
        
        if not cls.is_valid_shuar_text(normalized):
            raise ValidationError("Text contains invalid characters for Shuar language")
            
        return normalized
    
    @classmethod
    def detect_vocal_types(cls, text: str) -> dict:
        """Detect vocal types present in the text."""
        text_lower = text.lower()
        
        return {
            'has_oral_vowels': any(vowel in text_lower for vowel in cls.ORAL_VOWELS),
            'has_nasal_vowels': any(vowel in text_lower for vowel in cls.NASAL_VOWELS),
            'has_laryngealized_vowels': any(vowel in text_lower for vowel in cls.LARYNGEALIZED_VOWELS)
        }


class SpanishTextValidator:
    """Validator for Spanish text input."""
    
    @classmethod
    def is_valid_spanish_text(cls, text: str) -> bool:
        """Check if text appears to be Spanish."""
        if not text or not text.strip():
            return False
            
        # Basic Spanish character validation
        spanish_pattern = re.compile(r'^[a-záéíóúüñ\s\.,;:¡!¿?\-]+$', re.IGNORECASE)
        return bool(spanish_pattern.match(text.strip()))
    
    @classmethod
    def validate_spanish_text(cls, text: str, max_length: int = 500) -> str:
        """Validate and normalize Spanish text input."""
        if not text:
            raise ValidationError("Text cannot be empty")
            
        if len(text) > max_length:
            raise ValidationError(f"Text exceeds maximum length of {max_length} characters")
        
        normalized = text.strip()
        
        if not cls.is_valid_spanish_text(normalized):
            raise ValidationError("Text contains invalid characters for Spanish language")
            
        return normalized


def validate_rating(rating: int) -> int:
    """Validate feedback rating value."""
    if not isinstance(rating, int):
        raise ValidationError("Rating must be an integer")
        
    if rating < 1 or rating > 5:
        raise ValidationError("Rating must be between 1 and 5")
        
    return rating


def validate_comment(comment: Optional[str], max_length: int = 500) -> Optional[str]:
    """Validate feedback comment."""
    if comment is None:
        return None
        
    if len(comment.strip()) == 0:
        return None
        
    if len(comment) > max_length:
        raise ValidationError(f"Comment exceeds maximum length of {max_length} characters")
        
    return comment.strip()