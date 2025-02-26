"""This script is an entry-point for testing the game."""

import sys, os
sys.path.append(".")
from classes.player import get_test_player_1, get_test_player_2
from classes.match import Match
from classes.board import Board
from classes.command import Command

player_1 = get_test_player_1()
player_2 = get_test_player_2()
creature_1 = player_1.creatures[0]
creature_2 = player_2.creatures[0]

board = Board(10, 10)

game = Match(board, player_1, player_2)

# set creature positions automatically
# game.init_creature_positions()
# game.play_turn([
#     Command(creature_1, board[0][9], creature_1.actions[0], creature_2.position),
#     Command(creature_2, board[0][0], creature_2.actions[0], creature_1.position)
# ])

# set creature positions manually
creature_1.set_position(board[5][5])
creature_2.set_position(board[6][5])
game.play_turn([
    Command(creature_1, board[4][5], creature_1.actions[0], creature_2.position),
    Command(creature_2, board[4][5], creature_2.actions[0], creature_1.position)
])
