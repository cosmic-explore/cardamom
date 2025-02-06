class Command:
    def __init__(self, creature, move_target, action, action_target):
        self.creature = creature
        self.move_target = move_target
        self.action = action
        self.action_target = action_target
        
        self.move_path = creature.get_move_path(move_target)