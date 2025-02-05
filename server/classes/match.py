import os
from time import sleep
from game_logic.constants import TURN_LENGTH_SECONDS, TICKS_PER_TURN

class Match:
    def __init__(self, board, players):
        self.board = board
        self.players = players
        self.turn_number = 1

    def display_game(self):
        os.system("clear")
        print(f"Turn {self.turn_number}")
        print(self.board)

    def play_turn(self, move_paths):
        self.display_game()
        for tick in range (1, TICKS_PER_TURN):
            for path in move_paths:
                creature = path[0]
                moves = path[1]
                if tick < len(moves): 
                    creature.set_position(moves[tick])
            sleep(TURN_LENGTH_SECONDS / TICKS_PER_TURN)
            self.display_game()
        
        self.turn_number += 1
        self.display_game()