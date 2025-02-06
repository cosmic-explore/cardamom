import os
from math import floor
from time import sleep
from game_logic.constants import TURN_LENGTH_SECONDS, TICKS_PER_TURN

class Match:
    def __init__(self, board, player_1, player_2):
        self.board = board
        self.player_1 = player_1
        self.player_2 = player_2
        self.turn_number = 1

    def remove_fainted_commands(commands):
        return [command for command in commands if not command.creature.is_fainted]

    def display_game(self):
        os.system("clear")
        print(f"Turn {self.turn_number}")
        print(self.board)

    def init_creature_positions(self):
        """Place the players' creatures on the board when the game starts"""
        def init_player_creatures(player, y_pos):
            creature_spacing = floor(self.board.size_x / len(player.creatures))
            for index, creature in enumerate(player.creatures):
                creature.set_position(self.board[index * creature_spacing][y_pos])

        init_player_creatures(self.player_1, 0)
        init_player_creatures(self.player_2, self.board.size_y - 1)
        self.display_game()

    def play_turn(self, commands):
        self.display_game()

        # perform actions
        for command in commands:
            if command.creature.is_fainted:
                continue
            for pos in command.action.get_affected_positions(command.creature.position, command.action_target):
                if pos.creature is not None and pos.creature is not command.creature:
                    receiver = pos.creature
                    receiver.receive_action(command.action)
                    print("hit")
                    if receiver.is_fainted:
                        print("knock out")
        commands = Match.remove_fainted_commands(commands)

        self.display_game()

        # perform moves
        for tick in range (1, TICKS_PER_TURN):
            for command in commands:
                if tick < len(command.move_path):
                    command.creature.set_position(command.move_path[tick])
            sleep(TURN_LENGTH_SECONDS / TICKS_PER_TURN)
            self.display_game()
        
        self.turn_number += 1
        self.display_game()