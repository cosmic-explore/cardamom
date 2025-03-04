from math import sqrt
from .position import Position
from game_logic.util import flatten

class Board:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y

        self.__columns = [[Position(self, x, y) for y in range(size_y)] for x in range(size_x)]

    def __getitem__(self, key):
        """Expects to be called like board[x][y]. Returns the column at which
        to find position y."""
        # TODO: add error handling for out of bounds indexes
        return self.__columns[key]
    
    def __str__(self):
        def position_str(pos):
            return '[ ]' if pos.creature is None else f'[{pos.creature.nickname}]'
        
        board_representation = ''

        for y in reversed(range(self.size_y)):
            for x in range(self.size_x):
                board_representation += str(position_str(self.__columns[x][y]))
            board_representation += f' {y}'
            board_representation += '\n'

        board_representation += '\n '
        for x in range(self.size_x):
            board_representation += f'{x}  '

        return board_representation
    
    def get_distance(self, position_1, position_2):
        return abs(
            sqrt(
                ((position_2.x - position_1.x) ** 2) +
                ((position_2.y - position_1.y) ** 2)
            )
        )

    def get_positions_in_range(self, position, distance):
        # uses brute force rather than a pathing algorithm like BFS because
        # performance is not currently an issue and boards are always
        # rectangular
        return [
            pos for pos
            in flatten(self.__columns)
            # if pos is not position and 
            if self.get_distance(pos, position) <= distance
        ]

    def get_next_pos_in_path(self, start, destination):
        """Returns the adjacent position that is closest to the destination"""
        
        # is each creature moving at a different speeds better, or is it simpler to
        # have each creature simultaneously advancing one square at a time, with
        # creatures that are faster moving for longer? This is now an
        # implementation of the latter

        # should diagonals be treated as further away than verticals and
        # horizontals? Currently they are, and this sometimes leads to non-
        # intuitive paths
        
        if start is destination:
            return None

        next_pos = start
        for position in start.get_adjacent_positions():
            if self.get_distance(position, destination) < self.get_distance(next_pos, destination):
                next_pos = position

        return next_pos
