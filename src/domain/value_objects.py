"""
Value objects for similarity detection and content analysis.
"""
import hashlib
import re
from dataclasses import dataclass
from typing import Set


@dataclass(frozen=True)
class ContentFingerprint:
    """Immutable fingerprint for detecting duplicate content."""
    
    hash_value: str
    word_count: int
    key_terms: frozenset[str]
    
    @classmethod
    def from_text(cls, text: str) -> 'ContentFingerprint':
        """Create fingerprint from text content."""
        # Normalize text
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Extract words
        words = normalized.split()
        word_count = len(words)
        
        # Get significant terms (longer than 4 chars, not numbers)
        key_terms = frozenset(
            word for word in words
            if len(word) > 4 and not word.isdigit()
        )
        
        # Create hash
        hash_value = hashlib.sha256(normalized.encode()).hexdigest()[:16]
        
        return cls(
            hash_value=hash_value,
            word_count=word_count,
            key_terms=key_terms
        )
    
    def similarity_score(self, other: 'ContentFingerprint') -> float:
        """Calculate Jaccard similarity between fingerprints."""
        if not self.key_terms or not other.key_terms:
            return 0.0
        
        intersection = len(self.key_terms & other.key_terms)
        union = len(self.key_terms | other.key_terms)
        
        if union == 0:
            return 0.0
        
        return intersection / union


@dataclass(frozen=True)
class TitleSignature:
    """Normalized title signature for duplicate detection."""
    
    normalized: str
    word_set: frozenset[str]
    
    @classmethod
    def from_title(cls, title: str) -> 'TitleSignature':
        """Create signature from article title."""
        # Normalize: lowercase, remove punctuation, collapse whitespace
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Extract meaningful words (longer than 2 chars)
        words = frozenset(
            word for word in normalized.split()
            if len(word) > 2
        )
        
        return cls(
            normalized=normalized,
            word_set=words
        )
    
    def similarity_score(self, other: 'TitleSignature') -> float:
        """Calculate Jaccard similarity between title signatures."""
        if not self.word_set or not other.word_set:
            return 0.0
        
        intersection = len(self.word_set & other.word_set)
        union = len(self.word_set | other.word_set)
        
        if union == 0:
            return 0.0
        
        return intersection / union
