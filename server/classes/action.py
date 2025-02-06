class Action:
    def __init__(self, name, reach, power):
        self.name = name
        self.reach = reach
        self.power = power

    def get_affected_positions(self, start, destination):
        board = start.board
        if destination is None:
            # no destination means that action affects all squares within range
            return board.get_positions_in_range(start, self.reach)
        else:
            return set(board.get_travel_path(start, self.reach, destination))

def get_test_attack():
    return Action("test attack", 1, 1)