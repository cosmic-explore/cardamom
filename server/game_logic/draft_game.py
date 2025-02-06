import sys, os
sys.path.append(".")
from classes.match import Match
from classes.board import Board
from classes.creature import Creature
from classes.command import Command

board = Board(10, 10)
creature_1 = Creature(None, None, 1, "A")
creature_2 = Creature(None, None, 1, "B")
creature_1.set_position(board[9][0])
creature_2.set_position(board[9][1])

game = Match(board, [])
game.display_game()
game.play_turn([
    Command(creature_1, board[6][3], creature_1.actions[0], creature_2.position),
    Command(creature_2, board[6][3], creature_2.actions[0], creature_1.position)
])