import os
from uuid import uuid4
from math import floor
from time import sleep

class Match:
    def __init__(self, board, player_1, player_2, id=None, turn_number=1, active=True):
        self.id = id if id is not None else uuid4()
        self.board = board
        self.player_1 = player_1
        self.player_2 = player_2
        self.turn_number = turn_number
        self.active = active

    def remove_fainted_commands(commands):
        return [command for command in commands if not command.creature.is_fainted]

    def display_game(self):
        os.system("clear")
        print(f"Turn {self.turn_number}")
        print(self.board)
        sleep(0.5)

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
            if command.creature.is_fainted or command.action is None:
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
        # execute each move command until the creature runs out of moves
        do_moves_remain = True
        while do_moves_remain:
            do_moves_remain = False
            for command in commands:
                next_position = command.get_next_move()
                if next_position is not None:
                    do_moves_remain = True
                    command.creature.set_position(next_position)
            self.display_game()
        
        if self.check_game_over():
            self.end_game()
            return
        else:
            self.turn_number += 1
            self.display_game()

    def check_game_over(self):
        """Assumes there are only two players"""
        for player in [self.player_1, self.player_2]:
            if all(map(lambda creature: creature.is_fainted, player.creatures)):
                return True
        return False
    
    def end_game(self):
        """Assumes there are only two players"""
        # TODO: save the match history and result in database
        self.active = False
        print("Game Over")

        winner = self.get_winner()
        if winner is None:
            print("Draw")
        else:
            print(f"The winner is {winner.name}!")
            
    def get_winner(self):
        """Assumes there are only two players"""
        if self.active is True:
            return None
        
        for player in [self.player_1, self.player_2]:
            if any(map(lambda creature: not creature.is_fainted, player.creatures)):
                return player
        
        # everyone lost
        return None
    
    def to_simple_dict(self):
        """Aids the JSON serialization of Match objects. Expects to be called
        like json.dumps(match.to_simple_dict())."""
        def simplify_creature(creature):
            return {
                "id": str(creature.id),
                "species_id": creature.species_id,
                "player_id": creature.player_id,
                "level": creature.level,
                "nickname": creature.nickname,
                "position": None if creature.position is None else {
                    "x": creature.position.x,
                    "y": creature.position.y
                }
            }
        
        def simplify_player(player):
            return {
                "id": str(player.id),
                "name": player.name,
                "creatures": [simplify_creature(c) for c in player.creatures]
            }

        return {
            "id": str(self.id),
            "board": {
                "size_x": self.board.size_x,
                "size_y": self.board.size_y
            },
            "player_1": simplify_player(self.player_1),
            "player_2": simplify_player(self.player_2),
            "turn_number": self.turn_number,
            "active": self.active
        }
