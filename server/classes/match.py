import logging
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import ForeignKey, JSON, inspect
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableList
from typing import Any, Optional, List
from uuid import UUID, uuid4
from math import floor
from .base import db
from .board import Board
from .creature import CreatureState

class Match(db.Model):
    player_1_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("player.id"))
    player_2_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("player.id"))
    turn_number: Mapped[int] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False)
    history: Mapped[List[Any]] = mapped_column(MutableList.as_mutable(JSON), nullable=False)

    player_1 = relationship("Player", foreign_keys=[player_1_id])
    player_2 = relationship("Player", foreign_keys=[player_2_id])
    board: Mapped[Board] = relationship(back_populates="match")
    creature_states: Mapped[List[CreatureState]] = relationship("CreatureState", back_populates="match")
    
    def __init__(self, player_1, player_2, turn_number=0, active=True, id=None):
        self.id = id if id is not None else uuid4()
        self.player_1 = player_1
        self.player_2 = player_2
        self.turn_number = turn_number
        self.creature_states = []
        self.history = []
        self.active = active

    def start_game(self):
        logging.debug(f"Match {self.id} is starting!")
        self.init_creatures()
        self.store_tick() # stores turn 0
        self.turn_number = 1

    def init_creatures(self):
        """Place the players' creatures on the board when the game starts"""
        def init_player_creatures(player, y_pos):
            creature_spacing = floor(self.board.size_x / len(player.creatures))
            for index, creature in enumerate(player.creatures):
                creature_state = CreatureState(creature, self, None)
                db.session.add(creature_state)
                creature_state.set_position(self.board[index * creature_spacing][y_pos])
                logging.debug(f"Placed creature {creature.id} / state {creature_state.id} at [{creature_state.position.print_coords()}]")
                self.creature_states.append(creature_state)

        init_player_creatures(self.player_1, 0)
        init_player_creatures(self.player_2, self.board.size_y - 1)
        self.display_game()

    def remove_fainted_commands(commands):
        return [command for command in commands if not command.creature_state.is_fainted and command.move_target is not None]

    def display_game(self):
        logging.debug(f"Turn {self.turn_number}")
        logging.debug(self.board)

    def find_creature_in_match(self, creature_id):
        return next((c for c in self.player_1.creatures + self.player_2.creatures if str(c.id) == creature_id), None)

    def find_creature_state(self, creature_state_id):
        return next((cs for cs in self.creature_states if str(cs.id) == creature_state_id), None)

    def get_match_creatures(self):
        creatures = []
        if self.player_1:
            creatures.extend(self.player_1.creatures)
        if self.player_2:
            creatures.extend(self.player_2.creatures)
        return creatures

    def get_player_creature_states(self, player):
        return [cs for cs in self.creature_states if cs.creature.player_id == player.id]
    
    def has_player_lost(self, player):
        player_creature_states = self.get_player_creature_states(player)
        return all(map(lambda creature_state: creature_state.is_fainted, player_creature_states)) 

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

    def store_tick(self):
        """Stores a tick to the match's record of its turns. The index of history should be
        equivalent to the turn number"""
        if len(self.history) == self.turn_number:
            # add the current turn. Base case is when len(history) == 0 at turn 0.
            self.history.append([])
        
        logging.debug(f"Storing tick for turn {self.turn_number} in match {self.id}")
        # store a list of creature states in dict form
        self.history[self.turn_number].append({
            "board": self.board.to_simple_dict(),
            "creature_states": [{**cs.to_simple_dict(), **cs.creature.to_simple_dict()} for cs in self.creature_states]
        })

        def trick_sqlalchemy():
            """Forces SQLalchemy to think the history has been updated.
            The docs suggest creating a subclass of MutableList to track the changes of sublists, but it didn't work."""
            # TODO: Get the documentation's suggested method to work.
            # https://docs.sqlalchemy.org/en/20/orm/extensions/mutable.html#sqlalchemy.ext.mutable.MutableList
            self.history.append([])
            self.history.pop()
            logging.debug(f"Were changes to the match's history tracked by SQLAlchemy? {inspect(self).attrs.history.history.has_changes()}")
        trick_sqlalchemy()

    def play_turn(self, all_turn_commands):
        """All turn command is a dict of the command lists submitted by each player"""
        logging.debug(f"Adjudicating turn {self.turn_number} for match {self.id}")
        self.display_game()
        self.store_tick()

        # perform actions

        # TODO: determine a sensible order for creature actions to happen
        def perform_action(command):
            if command.creature_state.is_fainted or command.action is None:
                return
            for pos in command.action.get_affected_positions(command.creature_state.position, command.action_target):
                if pos.creature_state is not None and pos.creature_state.id != command.creature_state.id:
                    receiver = pos.creature_state
                    receiver.receive_action(command.action)
                    logging.debug(f"{receiver.creature.nickname} is hit")
                    if receiver.is_fainted:
                        logging.debug("knock out")

        for command in all_turn_commands["player_1"]:
            perform_action(command)
            self.store_tick()
        for command in all_turn_commands["player_2"]:
            perform_action(command)
            self.store_tick()
        
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
                    command.creature_state.set_position(next_position)
                    self.store_tick()
            self.display_game()
        
        if self.check_game_over():
            self.end_game()
        else:
            self.turn_number += 1
            self.display_game()

    def check_game_over(self):
        """Assumes there are only two players"""
        return self.has_player_lost(self.player_1) or self.has_player_lost(self.player_2)
    
    def end_game(self):
        """Assumes there are only two players"""
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
        
        if not self.has_player_lost(self.player_1) and self.has_player_lost(self.player_2):
            return self.player_1
        if not self.has_player_lost(self.player_2) and self.has_player_lost(self.player_1):
            return self.player_2

        # no one has lost yet
        return None
    
    def get_redis_channel(self):
        return f"MATCH_{self.id}"
    
    def to_simple_dict(self):
        """Aids the JSON serialization of Match objects. Expects to be called
        like json.dumps(match.to_simple_dict())."""
        return {
            "id": str(self.id),
            "player_1": None if self.player_1 is None else self.player_1.to_simple_dict(),
            "player_2": None if self.player_2 is None else self.player_2.to_simple_dict(),
            "turn_number": self.turn_number,
            "active": self.active,
            "board": self.board.to_simple_dict(),
            "creature_states": [cs.to_simple_dict() for cs in self.creature_states],
            "history": self.history
        }
