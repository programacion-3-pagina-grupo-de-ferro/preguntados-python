"""
Concrete Player implementation.
"""
import uuid
from collections import deque
from typing import Dict, Deque, List
from .base import AbstractPlayer

class Player(AbstractPlayer):
    """
    Principal class for the project.

    Attributes
    ----------
    name : str
        Public display name of the player. Must be unique across all players.
    score : int
        Total number of correct answers in the current session (0..10).
    total_answered : int
        Total number of questions answered in the current session (0..10).
    category_stats : Dict[str, int]
        Per-category count of correct answers: {category: correct_count}.
    history : Deque[str]
        A rolling window of recent roulette spins (categories).
    __uid : str
        Encapsulated internal unique ID (hidden / name-mangled).

    Notes
    -----
    This class inherits from AbstractPlayer (an abstract base class), satisfying
    the requirement of having at least one class inherit from a class abstracta.
    It includes more than five attributes, with __uid correctly encapsulated.
    """
    def __init__(self, name: str, categories: List[str]):
        self.name: str = name
        self.score: int = 0
        self.total_answered: int = 0
        self.category_stats: Dict[str, int] = {c: 0 for c in categories}
        self.history: Deque[str] = deque(maxlen=10)
        self.__uid: str = str(uuid.uuid4())  # encapsulated/private

    # ---------------- Properties / Encapsulation ----------------
    def get_id(self) -> str:
        """Return the internal unique identifier (encapsulated)."""
        return self.__uid

    # ---------------- Serialization ----------------
    def to_dict(self) -> dict:
        """Serialize Player to a dict for JSON persistence."""
        return {
            "id": self.__uid,
            "name": self.name,
            "score": self.score,
            "total_answered": self.total_answered,
            "category_stats": dict(self.category_stats),
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: dict, categories: List[str]) -> "Player":
        """
        Rehydrate a Player from a serialized dict.
        """
        obj = cls(name=data["name"], categories=categories)
        # restore state
        obj.score = data.get("score", 0)
        obj.total_answered = data.get("total_answered", 0)
        obj.category_stats.update(data.get("category_stats", {}))
        obj.history.extend(data.get("history", []))
        # careful: set private attribute using name-mangled name
        obj._Player__uid = data.get("id")  # type: ignore[attr-defined]
        return obj

    # ---------------- Game logic helpers ----------------
    def update_score(self, category: str, correct: bool) -> None:
        """
        Update the player's stats after answering a question.
        """
        self.total_answered += 1
        if category not in self.category_stats:
            self.category_stats[category] = 0
        if correct:
            self.score += 1
            self.category_stats[category] += 1
        self.history.append(category)
