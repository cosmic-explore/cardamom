import logging

logging.basicConfig(level=logging.DEBUG)

class Position:
    def __init__(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y
        self.__creature_id = None

    @property
    def creature_id(self):
        return self.__creature_id

    def __str__(self):
        return f'[{self.x},{self.y},{" " if self.creature_id is None else "X"}]'
    
    def is_same(self, position):
        """Assumes the compared position belongs to the same board"""
        return self.x == position.x and self.y == position.y

    def set_creature_id(self, new_creature_id):
        """This func should only be called by Creature.set_position"""

        if self.creature_id is None:
            self.__creature_id = new_creature_id
        elif new_creature_id is None:
            # Note: the creature's position should already be set to this one
            self.__creature_id = new_creature_id
        elif self.creature_id == new_creature_id:
            self.__creature_id = new_creature_id
        else:
            logging.debug("Warnimg: tried to place creature on a non-empty Position")

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
            "creature_id": self.creature_id
        }
    