"""
Question model.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Question:
    """
    Represents a single multiple-choice question.
    """
    category: str
    prompt: str
    options: List[str]
    answer_index: int  # 0..len(options)-1
