import logging

from .creature import CreatureState
from .action import Action

logging.basicConfig(level=logging.DEBUG)

class Command:
    def __init__(self, creature_state, move_target, action, action_target):
        self.creature_state = creature_state
        self.move_target = move_target
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
            match.find_creature_state(command_dict["creature_state_id"]),
            move_target,
            None if command_dict["action"] is None else Action.from_dict(command_dict["action"]),
            action_target
        )

    def get_next_move(self):
        return (
            self.creature_state.position.board.get_next_pos_in_path(
                self.creature_state.position, self.move_target
            )
        )
        
    def to_simple_dict(self):
        """Aids the JSON serialization of Command objects. Expects to be called
        like json.dumps(command.to_simple_dict())."""
        return {
            "creature_state_id": str(self.creature_state.id),
            "move_target": None if self.move_target is None else self.move_target.to_simple_dict(),
            "action": None if self.action is None else self.action.to_simple_dict(),
            "action_target":None if self.action_target is None else self.action_target.to_simple_dict()
        }