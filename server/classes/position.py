class Position:
    def __init__(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y
        self.__creature = None

    @property
    def creature(self):
        return self.__creature

    def __str__(self):
        return f'[{self.x},{self.y},{" " if self.creature is None else self.creature.nickname}]'
    
    def set_creature(self, new_creature):
        # it's this function's responsibility to ensure that position.creature
        # and creature.position always correspond.

        if self.creature is None:
            if new_creature is not None:
                self.__creature = new_creature
                new_creature.set_position(self)
        elif new_creature is None:
            if self.__creature.position is self:
                # the position is trying to clear without moving its creature first
                raise Exception("Dangling Creature")
            self.__creature = None
        else:
            if new_creature is self.creature:
                return
            print("Position is already occupied")
            return

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

    def to_simple_dict(self):
        """Aids the JSON serialization of Match objects. Expects to be called
        like json.dumps(position.to_simple_dict())."""
        return {
            "x": self.x,
            "y": self.y,
            "creature": None if self.creature is None else str(self.creature.id)
        }
    