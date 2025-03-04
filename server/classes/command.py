class Command:
    def __init__(self, creature, move_target, action, action_target):
        self.creature = creature
        self.move_target = move_target
        self.moves_remaining = creature.speed
        self.action = action
        self.action_target = action_target

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
            "creature_id": str(self.creature.id),
            "move_target": None if self.move_target is None else {
                "x": self.move_target.x,
                "y": self.move_target.y
            },
            "moves_remaining": self.moves_remaining,
            "action_id": str(self.action.id),
            "action_target": None if self.action_target is None else {
                "x": self.action_target.x,
                "y": self.action_target.y
            }
        }