from sqlalchemy.orm import Mapped, mapped_column
from .base import db
from uuid import uuid4

class Action(db.Model):
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    reach: Mapped[int] = mapped_column(nullable=False)
    power: Mapped[int] = mapped_column(nullable=False)
    
    def __init__(self, name, reach, power, id=None):
        self.id = uuid4() if id is None else id
        self.name = name
        self.reach = reach
        self.power = power

    @classmethod
    def from_dict(cls, action_dict):
        return Action(action_dict["name"], action_dict["reach"], action_dict["power"], id=action_dict["id"])

    def get_affected_positions(self, start, destination):
        board = start.board
        if destination is None:
            # no destination means that action affects all squares within range
            return board.get_positions_in_range(start, self.reach)
        else:
            # currently actions affect all positions between the user and the target
            affected_positions = []
            remaining_reach = self.reach
            next_pos = board.get_next_pos_in_path(start, destination)
            while next_pos is not None and remaining_reach > 0:
                affected_positions.append(next_pos)
                remaining_reach -= 1
                next_pos = board.get_next_pos_in_path(next_pos, destination)

            if destination not in affected_positions:
                print("Action failed to reach target")

            return affected_positions
        
    def to_simple_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "reach": self.reach,
            "power": self.power
        }

    @classmethod
    def from_dict(cls, simple_dict):
        return Action(
            simple_dict["name"],
            simple_dict["reach"],
            simple_dict["power"],
            id=simple_dict["id"]
        )
