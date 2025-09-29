import logging
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableList
from typing import Any, List
from uuid import UUID, uuid4
from .base import db
from .creature import CreatureState

class Position(db.Model):
    board_id: Mapped[UUID] = mapped_column(ForeignKey("board.id"), nullable=False)
    x: Mapped[int] = mapped_column(nullable=False)
    y: Mapped[int] = mapped_column(nullable=False)
    effects: Mapped[List[Any]] = mapped_column(MutableList.as_mutable(JSON), nullable=False)

    board = relationship("Board", back_populates="positions")
    creature_state: Mapped[CreatureState] = relationship("CreatureState", back_populates="position")

    __table_args__ = (UniqueConstraint("board_id", "x", "y"),)
    
    def __init__(self, board, x, y, creature_state=None, id=None):
        self.id = uuid4() if id is None else id
        self.board = board
        self.x = x
        self.y = y
        self.creature_state = creature_state
        self.effects = []

    def __str__(self):
        return f'[{self.x},{self.y},{" " if self.creature_state is None else "X"}]'
    
    def print_coords(self):
        return f"{self.x},{self.y}"
    
    def is_same(self, position):
        """Assumes the compared position belongs to the same board"""
        return self.x == position.x and self.y == position.y

    def get_adjacent_positions(self):
        low_bound_x = max(self.x - 1, 0)
        low_bound_y = max(self.y - 1, 0)
        high_bound_x = min(self.x + 1, self.board.size_x - 1)
        high_bound_y = min(self.y + 1, self.board.size_y - 1)
        adjacent_positions = []

        for x in range(low_bound_x, high_bound_x + 1):
            for y in range(low_bound_y, high_bound_y + 1):
                if x == self.x and y == self.y:
                    continue
                adjacent_positions.append(self.board[x][y])

        return adjacent_positions
    
    def clear_effects(self):
        self.effects = []

    def to_simple_dict(self):
        """Aids the JSON serialization of Match objects. Expects to be called
        like json.dumps(position.to_simple_dict())."""
        return {
            "id": str(self.id),
            "x": self.x,
            "y": self.y,
            "creature_state_id": None if self.creature_state is None else str(self.creature_state.id),
            "effects": self.effects
        }
    
    @classmethod
    def from_dict(cls, position_dict, board):
        position = Position(
            board,
            position_dict["x"],
            position_dict["y"],
            id=position_dict["id"]
        )
        position.effects = position_dict["effects"]
        if position_dict["creature_state_id"] is not None:
            for cs in board.match.creature_states:
                if cs.id == position["creature_state_id"]:
                    position.creature_state = cs
        return position
