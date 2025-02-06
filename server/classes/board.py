from math import sqrt, ceil
from .position import Position
from game_logic.util import flatten
from game_logic.constants import TICKS_PER_TURN

class Board:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y

        self.__columns = [[Position(self, x, y) for y in range(size_y)] for x in range(size_x)]
        self.creatures = []

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
            if pos is not position
            and self.get_distance(pos, position) <= distance
        ]

    def get_travel_path(self, start, travel_range, destination):
        if destination not in self.get_positions_in_range(start, travel_range):
            raise Exception("Destination out of range")

        travel_path = []
        distance = self.get_distance(start, destination)
        unit_vector = [
            (destination.x - start.x) / distance,
            (destination.y - start.y) / distance
        ]
        
        # is each creature moving at a different speeds better, or is it simpler to
        # have each creature simultaneously advancing one square at a time, with
        # creatures that are faster moving for longer? This is an implementation of
        # the former

        # should diagonals be treated as further away than verticals and
        # horizontals? Currently they are, and this sometimes leads to non-
        # intuitive paths

        # it might be best to remove the idea of ticks altogether, and instead just
        # calculate for collision based on trajectories while animating smoothly on
        # the frontend
        
        distance_per_tick = travel_range / TICKS_PER_TURN
        ticks_to_move = ceil(distance / distance_per_tick)

        # Finds positions at the given distances between starting and ending points
        for tick_pos in range(1, ticks_to_move):
            current_distance = distance_per_tick * tick_pos
            x_pos = round(start.x + (unit_vector[0] * current_distance))
            y_pos = round(start.y + (unit_vector[1] * current_distance))
            travel_path.append(self[x_pos][y_pos])
        
        return travel_path