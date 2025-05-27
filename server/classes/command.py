import logging

from .creature import Creature
from .action import Action

logging.basicConfig(level=logging.DEBUG)

class Command:
    def __init__(self, creature, move_target, action, action_target):
        self.creature = creature
        self.move_target = move_target
        self.moves_remaining = creature.speed
        self.action = action
        self.action_target = action_target

    @classmethod
    def from_dict_and_match(cls, command_dict, match):
        move_target = command_dict["move_target"]
        if move_target is not None:
            move_target = match.board[move_target["x"]][move_target["y"]]
        action_target = command_dict["action_target"]
        if action_target is not None:
            action_target = match.board[action_target["x"]][action_target["y"]]
        
        return Command(
            Creature.from_dict(command_dict["creature"], match=match),
            move_target,
            None if command_dict["action"] is None else Action.from_dict(command_dict["action"]),
            action_target
        )

    def get_next_move(self):
        if self.moves_remaining >= 1:
            self.moves_remaining -= 1
            return (
                self.creature.position.board.get_next_pos_in_path(
                    self.creature.position, self.move_target
                )
            )
        else:
            return None
        
    def to_simple_dict(self):
        """Aids the JSON serialization of Command objects. Expects to be called
        like json.dumps(command.to_simple_dict())."""
        return {
            # TODO: only store the ids of the creature and action when the DB is in place
            "creature": self.creature.to_simple_dict(),
            "move_target": None if self.move_target is None else self.move_target.to_simple_dict(),
            "moves_remaining": self.moves_remaining,
            "action": None if self.action is None else self.action.to_simple_dict(),
            "action_target":None if self.action_target is None else self.action_target.to_simple_dict()
        }