import logging
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import db
from .species import Species
from uuid import UUID, uuid4

class Creature(db.Model):
    nickname: Mapped[Optional[str]] = mapped_column()
    level: Mapped[int] = mapped_column(nullable=False)
    
    species_id: Mapped[UUID] = mapped_column(ForeignKey("species.id"), nullable=False)
    player_id: Mapped[UUID] = mapped_column(ForeignKey("player.id"), nullable=False)

    species = relationship("Species")
    player = relationship("Player")

    def __init__(self, species_id, player_id, level, nickname, id=None):
        self.id = self.id = uuid4() if id is None else id
        self.species_id = species_id
        self.player_id = player_id
        self.level = level
        self.nickname = nickname

    @property
    def max_hp(self):
        # TODO: define and implement level-based algorithm
        return self.species.base_hp
    
    @property
    def attack(self):
        # TODO: define and implement level-based algorithm
        return self.species.base_attack

    @property
    def speed(self):
        # TODO: define and implement level-based algorithm
        return self.species.base_speed

    @property
    def actions(self):
        # TODO: let each creature have its own action pool
        return self.species.actions
    
    def find_action_of_creature(self, action_id):
        return next((a for a in self.actions if str(a.id) == action_id), None)

    def to_simple_dict(self):
        return {
            "id": str(self.id),
            "species_id": str(self.species_id),
            "species": self.species.to_simple_dict(),
            "player_id": str(self.player_id),
            "level": self.level,
            "nickname": self.nickname,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "speed": self.speed,
            "actions": [a.to_simple_dict() for a in self.actions],
        }
    
    @classmethod
    def from_dict(cls, creature_dict):
        creature = Creature(
            creature_dict["species_id"],
            creature_dict["player_id"],
            creature_dict["level"],
            creature_dict["nickname"],
            id=creature_dict["id"]
        )
        creature.species = Species.from_dict(creature_dict["species"])
        return creature

class CreatureState(db.Model):
    """Class for the state of a creature within a given Match"""
    match_id: Mapped[UUID] = mapped_column(ForeignKey("match.id"), nullable=False)
    position_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("position.id"), unique=True)
    creature_id: Mapped[UUID] = mapped_column(ForeignKey("creature.id"), nullable=False)
    current_hp: Mapped[int] = mapped_column(nullable=False)

    match = relationship("Match")
    creature: Mapped[Creature] = relationship("Creature")
    position = relationship("Position", back_populates="creature_state")

    def __init__(self, creature, match, position, id=None, current_hp=None):
        self.id = uuid4() if id is None else id
        self.creature = creature
        self.match = match
        self.position = position
        self.current_hp = creature.max_hp if current_hp is None else current_hp

    @property
    def is_fainted(self):
        return self.current_hp <= 0

    def set_position(self, new_position):
        # handle creature being removed from board

        if new_position is None:
            logging.debug(f"Removing creature {self.creature_id} from the board")
            self.position = None
            # old_position.set_creature_state_id(None)

        # prevent invalid moves
        
        elif new_position.creature_state is not None and new_position.creature_state != self:
            logging.debug("Position is occupied")

        # handle a valid move

        else:
            logging.debug(f"Updating creature {self.creature_id} position to [{new_position.x},{new_position.y}]")
            # old_position = self.position

            # # remove creature from old position
            # if old_position is not None:
            #     old_position.set_creature_state_id(None)

            # add creature to new position 
            self.position = new_position
            # new_position.set_creature_state_id(self.id)

    def get_planned_move_path(self, destination):
        board = self.position.board
        path = []
        remaining_speed = self.creature.speed

        def find_path(board, path, current_pos, remaining_speed):
            next_pos = board.get_next_pos_in_path(current_pos, destination)
            if remaining_speed == 0 or next_pos is None:
                return path
            else:
                path.append(next_pos)
                remaining_speed -= 1
                return find_path(board, path, next_pos, remaining_speed)
            
        return find_path(board, path, self.position, remaining_speed)            

    def receive_action(self, action):
        # for now, the only type of actions are attacks
        # TODO: add a damage equation that factors in creature defense
        self.current_hp -= action.power
        if self.current_hp <= 0:
            self.remove_from_board()

    def remove_from_board(self):
        if self.position is not None:
            self.set_position(None)

    def to_simple_dict(self):
        return {
            "id": str(self.id),
            "creature_id": str(self.creature.id),
            "match_id": str(self.match_id),
            "current_hp": self.current_hp,
            "position": None if self.position is None else self.position.to_simple_dict()
        }
    
    @classmethod
    def from_dict(cls, creature_state_dict, match=None):
        creature_state = CreatureState(
            None, None, None,
            id=creature_state_dict["id"],
            current_hp=creature_state_dict["current_hp"]
        )
        creature_state.match_id = creature_state_dict["match_id"]        
        creature_state.creature_id = creature_state_dict["creature_id"]
        
        # hook up the relationships if possible
        if match is not None:
            # hook creature
            creature_state.creature = match.find_creature_in_match(creature_state.creature_id)
            # hook position
            if creature_state_dict["position"] is not None:
                board = match.board
                creature_state.set_position(
                    board[
                        creature_state_dict["position"]["x"]
                    ]
                    [
                        creature_state_dict["position"]["y"]
                    ]
                )
        
        return creature_state