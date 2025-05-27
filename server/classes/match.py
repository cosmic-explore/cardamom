import logging
from uuid import uuid4
from math import floor
from constants import TEST_MATCH_ID

logging.basicConfig(level=logging.DEBUG)

def player_info_dict(player):
    """Provides only the data necessary for the frontend"""

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
        logging.debug(f"Turn {self.turn_number}")
        logging.debug(self.board)

    def find_creature_in_match(self, creature_id):
        return next((c for c in self.player_1.creatures + self.player_2.creatures if c.id == creature_id), None)

    def get_player_number(self, player):
        if self.player_1 and self.player_1.name == player.name:
            return 1
        elif self.player_2 and self.player_2.name == player.name:
            return 2
        else:
            return None
        
    def is_player_in_match(self, player):
        return (self.player_1 and player.name == self.player_1.name) or (
            self.player_2 and player.name == self.player_2.name)

    def init_creature_positions(self):
        """Place the players' creatures on the board when the game starts"""
        def init_player_creatures(player, y_pos):
            creature_spacing = floor(self.board.size_x / len(player.creatures))
            for index, creature in enumerate(player.creatures):
                creature.set_position(self.board[index * creature_spacing][y_pos])

        init_player_creatures(self.player_1, 0)
        init_player_creatures(self.player_2, self.board.size_y - 1)
        self.display_game()

    def play_turn(self, all_turn_commands):
        """All turn command is a dict of the command lists submitted by each player"""
        logging.debug(f"Adjudicating turn {self.turn_number} for match {self.id}")
        self.display_game()

        # perform actions
        # TODO: determine a sensible order for creature actions to happen
        def perform_action(command):
            if command.creature.is_fainted or command.action is None:
                return
            logging.debug(command.creature.to_simple_dict())
            for pos in command.action.get_affected_positions(command.creature.position, command.action_target):
                if pos.creature_id is not None and pos.creature_id != command.creature.id:
                    receiver = self.find_creature_in_match(pos.creature_id)
                    receiver.receive_action(command.action)
                    logging.debug("hit")
                    if receiver.is_fainted:
                        logging.debug("knock out")

        for command in all_turn_commands["player_1"]:
            perform_action(command)
        for command in all_turn_commands["player_2"]:
            perform_action(command)
        
        # remove the remaning commands of creatures that fainted after actions
        all_turn_commands["player_1"] = Match.remove_fainted_commands(all_turn_commands["player_1"])
        all_turn_commands["player_2"] = Match.remove_fainted_commands(all_turn_commands["player_2"])

        self.display_game()

        # perform moves
        creature_moves = all_turn_commands["player_1"] + all_turn_commands["player_2"]
        # execute each move command until all creatures run out of moves
        do_moves_remain = True
        while do_moves_remain:
            do_moves_remain = False
            for command in creature_moves:
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
        logging.debug("Game Over")

        winner = self.get_winner()
        if winner is None:
            logging.debug("Draw")
        else:
            logging.debug(f"The winner is {winner.name}!")
            
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
        return {
            "id": str(self.id),
            "board": self.board.to_simple_dict(),
            "player_1": None if self.player_1 is None else self.player_1.to_simple_dict(),
            "player_2": None if self.player_2 is None else self.player_2.to_simple_dict(),
            "turn_number": self.turn_number,
            "active": self.active
        }
