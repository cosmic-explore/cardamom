import sys, os
sys.path.append(".")
from classes.match import Match
from classes.board import Board
from classes.creature import Creature

board = Board(10, 10)
creature_1 = Creature(None, None, 1, "A")
creature_2 = Creature(None, None, 1, "B")
creature_1.set_position(board[9][0])
creature_2.set_position(board[0][9])

game = Match(board, [])
game.display_game()
game.play_turn([
    board.get_creature_path(creature_1, board[6][3]),
    board.get_creature_path(creature_2, board[6][3])
])