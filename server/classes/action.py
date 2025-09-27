from sqlalchemy.orm import Mapped, mapped_column
from .base import db
from uuid import uuid4
from constants import ACTION_CAT_MELEE, ACTION_CAT_PROJECTILE, ACTION_CAT_BEAM, ACTION_CAT_RADIATE

class Action(db.Model):
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    reach: Mapped[int] = mapped_column(nullable=False)
    power: Mapped[int] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    
    def __init__(self, name, reach, power, category, id=None):
        self.id = uuid4() if id is None else id
        self.name = name
        self.reach = reach
        self.power = power
        self.category = category

    @classmethod
    def from_dict(cls, action_dict):
        return Action(action_dict["name"], action_dict["reach"], action_dict["power"], id=action_dict["id"])

    def get_affected_positions_at_tick(self, start, destination, tick_num):
        """Expects a tick number >= 1"""
        board = start.board

        if tick_num >= self.reach:
            return []

        if self.category == ACTION_CAT_MELEE:
            # hit a single position
            return [board.get_next_pos_in_path(start, destination)]
        elif self.category == ACTION_CAT_PROJECTILE:
            # hit the pos along the trajectory corresponding to the current tick
            path = board.get_full_path(start, destination)
            if tick_num >= len(path):
                return []
            return [path[tick_num]]
        elif self.category == ACTION_CAT_BEAM:
            # hit the pos along the trajectory corresponding to the current tick, and all previous positions
            path = board.get_full_path(start, destination)
            if tick_num >= len(path):
                return []
            return path[0 : tick_num + 1]
        elif self.category == ACTION_CAT_RADIATE:
            # hits all positions whose distance == tick_num
           return board.get_positions_at_distance(start, tick_num)
        else:
            # TODO: Throw exception
            return []

    def to_simple_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "reach": self.reach,
            "power": self.power,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, simple_dict):
        return Action(
            simple_dict["name"],
            simple_dict["reach"],
            simple_dict["power"],
            simple_dict["category"],
            id=simple_dict["id"]
        )
