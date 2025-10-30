"""
Base abstract entities for the Trivia game.
"""
from abc import ABC, abstractmethod

class AbstractPlayer(ABC):
    """
    Abstract base class that defines the minimum interface for a player-like entity.

    Methods
    -------
    get_id() -> str
        Returns the internal unique identifier (encapsulated in concrete classes).
    to_dict() -> dict
        Serializes the player to a JSON-serializable dictionary.
    update_score(category: str, correct: bool) -> None
        Records the result of a question and updates aggregate stats.
    """
    @abstractmethod
    def get_id(self) -> str:
        """Return the internal unique identifier for the player."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize the player to a dictionary."""
        raise NotImplementedError

    @abstractmethod
    def update_score(self, category: str, correct: bool) -> None:
        """Update the player's stats given a result for a category."""
        raise NotImplementedError
