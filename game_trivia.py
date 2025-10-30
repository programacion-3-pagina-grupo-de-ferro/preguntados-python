"""
Core game engine for the Trivia game.
"""
from __future__ import annotations
import json
import os
import random
import re
from queue import Queue
from typing import Dict, List, Tuple
from collections import deque

from models.player import Player
from models.player_tree import PlayerBST
from models.question import Question

CATEGORIES = ["Historia", "Ciencia", "Geografía", "Deporte"]

class GameEngine:
    """
    Orchestrates the game loop and persistence.
    """
    def __init__(self, data_dir: str):
        # paths
        self.data_dir = data_dir
        self.questions_path = os.path.join(data_dir, "questions.json")
        self.scoreboard_path = os.path.join(data_dir, "scoreboard.json")

        # core state
        self.players_bst: PlayerBST = PlayerBST.from_json(self.scoreboard_path, categories=CATEGORIES)
        self.questions: List[Question] = self._load_questions()
        self.pending: Queue[Question] = Queue()
        self.recent_spins: deque[str] = deque(maxlen=20)

    # ----------------- Loading -----------------
    def _load_questions(self) -> List[Question]:
        """
        Load questions from JSON.
        """
        with open(self.questions_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        out: List[Question] = []
        for cat, items in data.items():
            for row in items:
                out.append(Question(
                    category=cat,
                    prompt=row["prompt"],
                    options=row["options"],
                    answer_index=row["answer_index"],
                ))
        return out

    # ----------------- Players CRUD -----------------
    def create_player(self, name: str) -> Player:
        """
        Create a new player with validation. Raises ValueError if invalid.
        """
        name = name.strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_ ]{2,30}", name):
            raise ValueError("Nombre inválido: 2-30 caracteres alfanuméricos, espacios o _.")
        if self.players_bst.read(name) is not None:
            raise ValueError(f"El nombre '{name}' ya está en uso.")
        p = Player(name=name, categories=CATEGORIES)
        self.players_bst.create(p)
        self._persist()
        return p

    def read_player(self, name: str) -> Player | None:
        return self.players_bst.read(name)

    def update_player(self, name: str, new_name: str | None = None) -> bool:
        """
        Update a player's name (example of Update).
        """
        if new_name:
            new_name = new_name.strip()
            if self.players_bst.read(new_name):
                raise ValueError(f"El nombre '{new_name}' ya está en uso.")
        def _do(p: Player):
            if new_name:
                p.name = new_name
        ok = self.players_bst.update(name, _do)
        if ok:
            # If rename, we need to delete+insert to preserve BST invariant
            if new_name and name != new_name:
                player = self.players_bst.read(new_name)  # after update we can't retrieve directly
                # Rebuild: remove old node and reinsert with new key
                temp = player
                self.players_bst.delete(name)
                if temp: self.players_bst.create(temp)
            self._persist()
        return ok

    def delete_player(self, name: str) -> bool:
        ok = self.players_bst.delete(name)
        if ok:
            self._persist()
        return ok

    def _persist(self) -> None:
        """Persist current players to JSON."""
        self.players_bst.to_json(self.scoreboard_path)

    # ----------------- Game logic -----------------
    def _spin_roulette(self) -> str:
        """
        Simulate a roulette spin among the 4 categories.
        """
        cat = random.choice(CATEGORIES)
        self.recent_spins.append(cat)
        return cat

    def _draw_question(self, category: str) -> Question:
        """
        Select a random question by category.
        """
        options = [q for q in self.questions if q.category == category]
        return random.choice(options)

    def play_round(self, player: Player, total_questions: int = 10) -> Player:
        """
        Conduct a round of `total_questions` with roulette-based category selection.
        """
        for _ in range(total_questions):
            cat = self._spin_roulette()
            player.history.append(cat)
            q = self._draw_question(cat)
            self.pending.put(q)
            # In GUI mode the question is served interactively; here we return the player afterwards.
        self._persist()
        return player

    def record_answer(self, player: Player, q: Question, answer_index: int) -> bool:
        """
        Record the user's answer and update stats.
        """
        correct = (answer_index == q.answer_index)
        player.update_score(q.category, correct)
        self._persist()
        return correct

    def get_ranking(self) -> List[Dict[str, any]]:
        """
        Compute ranking snapshot (sorted by score desc, name asc).
        """
        return self.players_bst.ranking()
