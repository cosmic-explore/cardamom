import sys, os
sys.path.append(".")
from classes.player import get_test_player_1, get_test_player_2
from classes.match import Match
from classes.board import Board
from classes.command import Command

player_1 = get_test_player_1()
player_2 = get_test_player_2()

board = Board(10, 10)

game = Match(board, player_1, player_2)
game.init_creature_positions()


# game.play_turn([
#     Command(creature_1, board[6][3], creature_1.actions[0], creature_2.position),
#     Command(creature_2, board[6][3], creature_2.actions[0], creature_1.position)
# ])