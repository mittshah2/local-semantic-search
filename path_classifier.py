"""
Path Classifier Module

Uses Factory Pattern to allow easy swapping of classification strategies.
Currently implements a heuristic-based classifier, but can be extended
with ML-based classifiers in the future.
"""

import os
import re
from abc import ABC, abstractmethod
from settings import (
    EXCLUDED_PATTERNS,
    EXCLUDED_EXTENSIONS,
    RELEVANCE_THRESHOLD,
    CLASSIFIER_TYPE,
    POSITIVE_EXTENSIONS,
    POSITIVE_NAMES,
    POSITIVE_FOLDERS,
    EXCLUDED_PATHS,
)


class PathClassifierBase(ABC):
    """Abstract base class for path classifiers."""
    
    @abstractmethod
    def is_relevant(self, path: str) -> bool:
        """
        Determine if a path is relevant for indexing.
        
        Args:
            path: Full file/folder path
            
        Returns:
            True if the path should be indexed, False otherwise
        """
        pass
    
    def matches_excluded_pattern(self, path: str) -> bool:
        """
        Check if path matches any excluded pattern.
        
        Args:
            path: Full file/folder path
            
        Returns:
            True if path should be excluded
        """
        path_lower = path.lower()
        
        # Check absolute excluded paths
        for excluded in EXCLUDED_PATHS:
            if path_lower.startswith(excluded.lower()):
                return True

        path_parts = path_lower.replace('/', '\\').split('\\')
        filename = os.path.basename(path)

        # Check hidden files/folders
        if filename.startswith('.'):
            return True
        
        # Check each path component against patterns
        for part in path_parts:
            for pattern in EXCLUDED_PATTERNS:
                if pattern.lower() in part:
                    return True
        
        # Check file extension
        _, ext = os.path.splitext(path_lower)
        if ext in [e.lower() for e in EXCLUDED_EXTENSIONS]:
            return True
            
        return False


class HeuristicClassifier(PathClassifierBase):
    """
    Heuristic-based path classifier.
    
    Analyzes path structure and naming to determine relevance
    without accessing file contents.
    """
    
    # Negative signals - patterns that indicate generated/irrelevant content
    NEGATIVE_PATTERNS = [
        r'^[a-f0-9]{32,}$',  # Hash-like names
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',  # UUIDs
        r'^\d+$',  # Pure numbers
        r'^_+',  # Leading underscores
    ]
    
    def __init__(self, threshold: float = RELEVANCE_THRESHOLD):
        self.threshold = threshold
        self._negative_regex = [re.compile(p, re.IGNORECASE) for p in self.NEGATIVE_PATTERNS]
    
    def is_relevant(self, path: str) -> bool:
        """
        Determine if path is relevant using heuristic scoring.
        
        Returns True if the path should be indexed.
        """
        # First check excluded patterns (hard filter)
        if self.matches_excluded_pattern(path):
            return False
        
        # Calculate relevance score
        score = self._calculate_score(path)
        return score >= self.threshold
    
    def _calculate_score(self, path: str) -> float:
        """
        Calculate a relevance score for the path.
        
        Score ranges from 0.0 (not relevant) to 1.0 (highly relevant).
        """
        score = 0.5  # Start neutral
        
        path_parts = path.replace('/', '\\').split('\\')
        filename = path_parts[-1] if path_parts else ''
        name_lower = filename.lower()
        name_without_ext = os.path.splitext(name_lower)[0]
        _, ext = os.path.splitext(name_lower)
        
        # Positive: Good extension
        if ext in POSITIVE_EXTENSIONS:
            score += 0.2
        
        # Positive: Meaningful name
        if name_without_ext in POSITIVE_NAMES:
            score += 0.15
        
        # Positive: In user-friendly folder
        for folder in POSITIVE_FOLDERS:
            if folder in [p.lower() for p in path_parts]:
                score += 0.1
                break
        
        # Negative: Hidden files/folders (starting with .)
        if filename.startswith('.'):
            score -= 0.3
        
        # Negative: Very deep nesting (more than 8 levels)
        if len(path_parts) > 8:
            score -= 0.1
        
        # Negative: Looks like generated/hash name
        for regex in self._negative_regex:
            if regex.match(name_without_ext):
                score -= 0.3
                break
        
        # Negative: Very short or very long names
        if len(name_without_ext) < 2:
            score -= 0.1
        elif len(name_without_ext) > 100:
            score -= 0.1
        
        # Clamp score to [0, 1]
        return max(0.0, min(1.0, score))


class ClassifierFactory:
    """
    Factory for creating path classifiers.
    
    Usage:
        classifier = ClassifierFactory.create('heuristic')
        if classifier.is_relevant(path):
            # index the path
    """
    
    _classifiers = {
        'heuristic': HeuristicClassifier,
        # Future: 'ml': MLClassifier,
    }
    
    @classmethod
    def create(cls, classifier_type: str = CLASSIFIER_TYPE) -> PathClassifierBase:
        """
        Create a classifier instance.
        
        Args:
            classifier_type: Type of classifier ('heuristic', 'ml', etc.)
            
        Returns:
            An instance of the requested classifier
            
        Raises:
            ValueError: If classifier type is not supported
        """
        if classifier_type not in cls._classifiers:
            available = ', '.join(cls._classifiers.keys())
            raise ValueError(f"Unknown classifier type: {classifier_type}. Available: {available}")
        
        return cls._classifiers[classifier_type]()
    
    @classmethod
    def register(cls, name: str, classifier_class: type):
        """
        Register a new classifier type.
        
        Args:
            name: Name to register the classifier under
            classifier_class: The classifier class (must inherit from PathClassifierBase)
        """
        if not issubclass(classifier_class, PathClassifierBase):
            raise TypeError("Classifier must inherit from PathClassifierBase")
        cls._classifiers[name] = classifier_class


# Default classifier instance for convenience
def get_classifier() -> PathClassifierBase:
    """Get the default classifier based on settings."""
    return ClassifierFactory.create()
