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

    def remove_fainted_commands(commands):
        return [command for command in commands if not command.creature.is_fainted]

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