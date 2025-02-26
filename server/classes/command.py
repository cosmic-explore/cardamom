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
