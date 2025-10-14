import logging

logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, reconstructor
from typing import List, Optional
from uuid import UUID, uuid4
from .base import db
from .position import Position
from game_logic.util import flatten


class Board(db.Model):
    # "Optional" in the type annotation allows the python Board to be initialized
    #  without a match, but not committed to db until it has a match
    match_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("match.id"), nullable=False
    )
    size_x: Mapped[int] = mapped_column(nullable=False)
    size_y: Mapped[int] = mapped_column(nullable=False)

    match = relationship("Match", single_parent=True, back_populates="board")
    positions: Mapped[List[Position]] = relationship(
        "Position", single_parent=True, back_populates="board"
    )

    __table_args__ = (UniqueConstraint("match_id"),)

    def __init__(self, size_x, size_y, match=None, id=None):
        self.id = uuid4() if id is None else id
        self.size_x = size_x
        self.size_y = size_y
        self.match = match

        self.columns = [
            [Position(self, x, y) for y in range(size_y)] for x in range(size_x)
        ]

    @reconstructor
    def init_on_load(self):
        """reconstruct the columns when the Board is pulled from the DB"""
        self.columns = [None] * self.size_x
        for row_num in range(len(self.columns)):
            # careful to create a new array instance for each row rather than reference
            self.columns[row_num] = [None] * self.size_y

        for pos in self.positions:
            self.columns[pos.x][pos.y] = pos

    def __getitem__(self, key):
        """Expects to be called like board[x][y]. Returns the column at which
        to find position y."""
        # TODO: add error handling for out of bounds indexes
        return self.columns[key]

    def __str__(self):
        def position_str(pos):
            return "[ ]" if pos.creature_state is None else f"[X]"

        board_representation = "\n"

        for y in reversed(range(self.size_y)):
            for x in range(self.size_x):
                board_representation += str(position_str(self.columns[x][y]))
            board_representation += f" {y}"
            board_representation += "\n"

        board_representation += "\n "
        for x in range(self.size_x):
            board_representation += f"{x}  "

        return board_representation

    def get_distance(self, position_1, position_2):
        """Returns the distance between two positions. A diagonally adjacent
        tile is treated as the same distance as a horizontal or vertical tile.
        Because diagonal movement is allowed, the distance is effectively the greater
        of the horizontal & vertical distance."""
        diff_x = abs(position_1.x - position_2.x)
        diff_y = abs(position_1.y - position_2.y)
        return max([diff_x, diff_y])

    def get_positions_in_range(self, position, distance):
        # uses brute force rather than a pathing algorithm like BFS because
        # performance is not an issue and boards are always rectangular
        return [
            pos
            for pos in flatten(self.columns)
            if pos is not position and self.get_distance(pos, position) <= distance
        ]

    def get_positions_at_distance(self, position, distance):
        return [
            pos
            for pos in flatten(self.columns)
            if self.get_distance(pos, position) == distance
        ]

    def get_next_pos_in_path(self, start, destination):
        """Returns the adjacent position that is closest to the destination"""
        if start is destination or destination is None:
            return None

        next_pos = start
        for position in start.get_adjacent_positions():
            current_distance = self.get_distance(position, destination)
            lowest_distance = self.get_distance(next_pos, destination)

            if current_distance < lowest_distance:
                next_pos = position

            elif current_distance == lowest_distance:
                # there are cases in which a diagonal pos and a vertical/horizontal pos have an equal distance
                # to the destination, so, in those cases, favor the horizontal/vertical path over the diagonal
                # for consistency and predictability.
                if (
                    abs(position.x - destination.x) < abs(next_pos.x - destination.x)
                ) or (
                    abs(position.y - destination.y) < abs(next_pos.y - destination.y)
                ):
                    next_pos = position

        return next_pos

    def get_full_path(self, start, destination):
        """Returns an array of positions between start (exclusive) and destination (inclusive)"""
        path = []
        current_position = self.get_next_pos_in_path(start, destination)
        while current_position != None:
            path.append(current_position)
            current_position = self.get_next_pos_in_path(current_position, destination)
        return path

    def clear_all_position_effects(self):
        for pos in self.positions:
            pos.clear_effects()

    def to_simple_dict(self):
        """Aids the JSON serialization of Match objects. Expects to be called
        like json.dumps(board.to_simple_dict())."""
        return {
            "id": str(self.id),
            "size_x": self.size_x,
            "size_y": self.size_y,
            "columns": [[pos.to_simple_dict() for pos in col] for col in self.columns],
        }
