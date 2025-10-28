"""Word domain entity representing Shuar vocabulary."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from app.core.shared.exceptions import ValidationError


class VocalType(Enum):
    """Types of vocals in Shuar phonology."""
    ORAL = "oral"
    NASAL = "nasal"
    LARYNGEALIZED = "laryngealized"


class WordType(Enum):
    """Grammatical types of words."""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    CONJUNCTION = "conjunction"
    PREPOSITION = "preposition"
    INTERJECTION = "interjection"


@dataclass
class PhonologicalInfo:
    """Phonological information for a Shuar word."""
    ipa_transcription: str
    has_nasal_vowels: bool = False
    has_laryngealized_vowels: bool = False
    vocal_types_present: List[VocalType] = field(default_factory=list)
    number_of_syllables: int = 0
    syllable_pattern: Optional[str] = None
    
    def __post_init__(self):
        """Validate phonological information after initialization."""
        if not self.ipa_transcription:
            raise ValidationError("IPA transcription is required")
        
        if self.number_of_syllables < 0:
            raise ValidationError("Number of syllables cannot be negative")


@dataclass
class MorphologicalInfo:
    """Morphological information for a Shuar word."""
    root_word: str
    is_compound: bool = False
    compound_components: List[str] = field(default_factory=list)
    applied_suffixes: List[str] = field(default_factory=list)
    morphological_analysis: Optional[str] = None
    
    def __post_init__(self):
        """Validate morphological information after initialization."""
        if not self.root_word:
            raise ValidationError("Root word is required")
        
        if self.is_compound and len(self.compound_components) < 2:
            raise ValidationError("Compound words must have at least 2 components")


@dataclass
class Word:
    """Domain entity representing a Shuar word with complete linguistic information."""
    
    id: UUID = field(default_factory=uuid4)
    shuar_text: str = ""
    spanish_translation: str = ""
    word_type: Optional[WordType] = None
    phonological_info: Optional[PhonologicalInfo] = None
    morphological_info: Optional[MorphologicalInfo] = None
    definition_extended: Optional[str] = None
    usage_examples: List[Dict[str, str]] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    cultural_notes: Optional[str] = None
    dialect_variations: List[Dict[str, str]] = field(default_factory=list)
    frequency_score: int = 0
    confidence_level: float = 0.5
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate word entity after initialization."""
        self._validate_required_fields()
        self._validate_confidence_level()
        self._validate_frequency_score()
    
    def _validate_required_fields(self):
        """Validate that required fields are present."""
        if not self.shuar_text or not self.shuar_text.strip():
            raise ValidationError("Shuar text is required")
        
        if not self.spanish_translation or not self.spanish_translation.strip():
            raise ValidationError("Spanish translation is required")
    
    def _validate_confidence_level(self):
        """Validate confidence level is within valid range."""
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
    
    def _validate_frequency_score(self):
        """Validate frequency score is non-negative."""
        if self.frequency_score < 0:
            raise ValidationError("Frequency score cannot be negative")
    
    def update_translation(self, new_translation: str) -> None:
        """Update the Spanish translation."""
        if not new_translation or not new_translation.strip():
            raise ValidationError("Translation cannot be empty")
        
        self.spanish_translation = new_translation.strip()
        self.updated_at = datetime.now()
    
    def add_usage_example(self, shuar_example: str, spanish_example: str, context: Optional[str] = None) -> None:
        """Add a usage example for the word."""
        if not shuar_example or not spanish_example:
            raise ValidationError("Both Shuar and Spanish examples are required")
        
        example = {
            "shuar": shuar_example.strip(),
            "spanish": spanish_example.strip(),
            "context": context.strip() if context else None
        }
        
        self.usage_examples.append(example)
        self.updated_at = datetime.now()
    
    def add_synonym(self, synonym: str) -> None:
        """Add a synonym in Shuar."""
        if not synonym or not synonym.strip():
            raise ValidationError("Synonym cannot be empty")
        
        synonym = synonym.strip()
        if synonym not in self.synonyms:
            self.synonyms.append(synonym)
            self.updated_at = datetime.now()
    
    def add_antonym(self, antonym: str) -> None:
        """Add an antonym in Shuar."""
        if not antonym or not antonym.strip():
            raise ValidationError("Antonym cannot be empty")
        
        antonym = antonym.strip()
        if antonym not in self.antonyms:
            self.antonyms.append(antonym)
            self.updated_at = datetime.now()
    
    def update_phonological_info(self, phonological_info: PhonologicalInfo) -> None:
        """Update phonological information."""
        self.phonological_info = phonological_info
        self.updated_at = datetime.now()
    
    def update_morphological_info(self, morphological_info: MorphologicalInfo) -> None:
        """Update morphological information."""
        self.morphological_info = morphological_info
        self.updated_at = datetime.now()
    
    def increment_frequency(self) -> None:
        """Increment the frequency score when word is used."""
        self.frequency_score += 1
        self.updated_at = datetime.now()
    
    def verify_word(self) -> None:
        """Mark the word as verified by an expert."""
        self.is_verified = True
        self.updated_at = datetime.now()
    
    def update_confidence(self, new_confidence: float) -> None:
        """Update confidence level based on community feedback."""
        if not 0.0 <= new_confidence <= 1.0:
            raise ValidationError("Confidence level must be between 0.0 and 1.0")
        
        self.confidence_level = new_confidence
        self.updated_at = datetime.now()
    
    def has_vocal_type(self, vocal_type: VocalType) -> bool:
        """Check if the word contains a specific vocal type."""
        if not self.phonological_info:
            return False
        
        return vocal_type in self.phonological_info.vocal_types_present
    
    def is_compound_word(self) -> bool:
        """Check if the word is a compound word."""
        return (self.morphological_info is not None and 
                self.morphological_info.is_compound)
    
    def get_root_word(self) -> Optional[str]:
        """Get the root word if morphological info is available."""
        if self.morphological_info:
            return self.morphological_info.root_word
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert word entity to dictionary representation."""
        return {
            "id": str(self.id),
            "shuar_text": self.shuar_text,
            "spanish_translation": self.spanish_translation,
            "word_type": self.word_type.value if self.word_type else None,
            "phonological_info": {
                "ipa_transcription": self.phonological_info.ipa_transcription,
                "has_nasal_vowels": self.phonological_info.has_nasal_vowels,
                "has_laryngealized_vowels": self.phonological_info.has_laryngealized_vowels,
                "vocal_types_present": [vt.value for vt in self.phonological_info.vocal_types_present],
                "number_of_syllables": self.phonological_info.number_of_syllables,
                "syllable_pattern": self.phonological_info.syllable_pattern
            } if self.phonological_info else None,
            "morphological_info": {
                "root_word": self.morphological_info.root_word,
                "is_compound": self.morphological_info.is_compound,
                "compound_components": self.morphological_info.compound_components,
                "applied_suffixes": self.morphological_info.applied_suffixes,
                "morphological_analysis": self.morphological_info.morphological_analysis
            } if self.morphological_info else None,
            "definition_extended": self.definition_extended,
            "usage_examples": self.usage_examples,
            "synonyms": self.synonyms,
            "antonyms": self.antonyms,
            "cultural_notes": self.cultural_notes,
            "dialect_variations": self.dialect_variations,
            "frequency_score": self.frequency_score,
            "confidence_level": self.confidence_level,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }