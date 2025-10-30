"""
Binary Search Tree (BST) over Player.name to perform full CRUD.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Callable, Any, Dict
import json
import os
from .player import Player

@dataclass
class _Node:
    key: str
    value: Player
    left: Optional["_Node"] = None
    right: Optional["_Node"] = None

class PlayerBST:
    """
    BST keyed by Player.name. Provides CRUD + traversal utilities.

    Methods
    -------
    create(player: Player) -> None
    read(name: str) -> Optional[Player]
    update(name: str, update_fn: Callable[[Player], Any]) -> bool
    delete(name: str) -> bool
    inorder() -> List[Player]
    to_json(path: str) -> None
    from_json(path: str, categories: List[str]) -> 'PlayerBST'
    """
    def __init__(self) -> None:
        self._root: Optional[_Node] = None

    # ------------ Core BST ops ------------
    def create(self, player: Player) -> None:
        """Insert a new player. Raises ValueError if name exists."""
        def _insert(node: Optional[_Node], key: str, value: Player) -> _Node:
            if node is None:
                return _Node(key, value)
            if key == node.key:
                raise ValueError(f"El jugador '{key}' ya existe.")
            if key < node.key:
                node.left = _insert(node.left, key, value)
            else:
                node.right = _insert(node.right, key, value)
            return node
        self._root = _insert(self._root, player.name, player)

    def read(self, name: str) -> Optional[Player]:
        """Retrieve a player by name."""
        node = self._root
        while node:
            if name == node.key:
                return node.value
            node = node.left if name < node.key else node.right
        return None

    def update(self, name: str, update_fn: Callable[[Player], Any]) -> bool:
        """Apply a function to the Player if it exists."""
        p = self.read(name)
        if p is None:
            return False
        update_fn(p)
        return True

    def delete(self, name: str) -> bool:
        """Remove a player by name. Returns True if it existed."""
        def _delete(node: Optional[_Node], key: str) -> (Optional[_Node], bool):
            if node is None:
                return None, False
            if key < node.key:
                node.left, ok = _delete(node.left, key)
                return node, ok
            if key > node.key:
                node.right, ok = _delete(node.right, key)
                return node, ok
            # found
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True
            # two children: inorder successor
            succ_parent = node
            succ = node.right
            while succ.left:
                succ_parent = succ
                succ = succ.left
            node.key, node.value = succ.key, succ.value
            if succ_parent.left == succ:
                succ_parent.left = succ.right
            else:
                succ_parent.right = succ.right
            return node, True
        self._root, ok = _delete(self._root, name)
        return ok

    def inorder(self) -> List[Player]:
        """Return all players in-order by name."""
        out: List[Player] = []
        def _traverse(n: Optional[_Node]) -> None:
            if not n: return
            _traverse(n.left); out.append(n.value); _traverse(n.right)
        _traverse(self._root)
        return out

    # ------------ Persistence ------------
    def to_json(self, path: str) -> None:
        """Persist all players to a JSON file (list of serialized players)."""
        data = [p.to_dict() for p in self.inorder()]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, path: str, categories: List[str]) -> "PlayerBST":
        """Load players (if any) from JSON file into a BST."""
        bst = cls()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for row in data:
                    # Back-compat with any prior format
                    p = Player.from_dict(row, categories=categories)
                    bst.create(p)
            except Exception:
                # On any parse error, start fresh
                pass
        return bst

    # ------------ Utilities ------------
    def ranking(self) -> List[Dict[str, any]]:
        """Return players ordered by score desc, then by name asc."""
        players = self.inorder()
        players.sort(key=lambda p: (-p.score, p.name.lower()))
        return [
            {
                "name": p.name,
                "score": p.score,
                "answered": p.total_answered,
                "category_stats": p.category_stats
            }
            for p in players
        ]
