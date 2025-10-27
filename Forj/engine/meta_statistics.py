import random
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class StatisticRange:
    min_val: float
    mode: float
    max_val: float
    q1: Optional[float] = None
    q3: Optional[float] = None

    def __post_init__(self):
        # If quartiles not provided, calculate them based on min/mode/max
        if self.q1 is None:
            self.q1 = self.min_val + (self.mode - self.min_val) * 0.25
        if self.q3 is None:
            self.q3 = self.mode + (self.max_val - self.mode) * 0.25

    def sample(self) -> float:
        """Sample a value from a triangular distribution."""
        # Using triangular distribution between min, mode, max
        return random.triangular(self.min_val, self.max_val, self.mode)

class MetaStatistics:
    def __init__(self):
        self.statistics: Dict[str, StatisticRange] = {
            'word_count': StatisticRange(
                min_val=5,    # Minimum words
                mode=15,      # Most common word count
                max_val=50     # Maximum words
            ),
            'sentiment': StatisticRange(
                min_val=0.0,  # Very negative
                mode=0.7,     # Generally positive
                max_val=1.0,   # Very positive
                q1=0.3,       # First quartile
                q3=0.9        # Third quartile
            ),
            'formality': StatisticRange(
                min_val=0.0,  # Very informal
                mode=0.7,     # Somewhat formal
                max_val=1.0    # Very formal
            )
        }
    
    def get_statistic(self, name: str) -> float:
        """Get a sampled value for a specific statistic."""
        if name not in self.statistics:
            raise ValueError(f"Unknown statistic: {name}")
        return self.statistics[name].sample()
    
    def get_all_statistics(self) -> Dict[str, float]:
        """Get sampled values for all statistics."""
        return {name: self.get_statistic(name) for name in self.statistics}
    
    def update_from_feedback(self, feedback: Dict[str, Any]):
        """Update statistics based on feedback.
        
        Args:
            feedback: Dictionary containing feedback on samples with their statistics
        """
        # This is a simplified version - in practice, you'd want to analyze
        # which statistics led to better/worse feedback and adjust accordingly
        pass
    
    def get_prompt_modifiers(self) -> str:
        """Get text modifiers to add to the prompt based on current statistics."""
        stats = self.get_all_statistics()
        
        modifiers = []
        
        # Word count guidance
        word_count = stats['word_count']
        if word_count < 10:
            modifiers.append("Use very concise language.")
        elif word_count > 30:
            modifiers.append("Use detailed and descriptive language.")
        
        # Sentiment guidance
        sentiment = stats['sentiment']
        if sentiment < 0.3:
            modifiers.append("The tone should be negative.")
        elif sentiment < 0.6:
            modifiers.append("The tone should be neutral.")
        else:
            modifiers.append("The tone should be positive.")
        
        # Formality guidance
        formality = stats['formality']
        if formality < 0.3:
            modifiers.append("Use casual, conversational language.")
        elif formality > 0.7:
            modifiers.append("Use formal, professional language.")
        
        return " ".join(modifiers)
