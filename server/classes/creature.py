import logging

from uuid import uuid4
from .species import get_test_species

logging.basicConfig(level=logging.DEBUG)

class Creature:
    def __init__(self, species_id, player_id, level, nickname, id=None):
        self.id = id if id is not None else uuid4()
        self.species_id = species_id
        self.player_id = player_id
        self.level = level
        self.nickname = nickname
        self.__init_from_species(species_id, level)
        
        self.__position = None

    @property
    def position(self):
        return self.__position

    @property
    def is_fainted(self):
        return self.current_hp <= 0

    def __init_from_species(self, species_id, level):
        # TODO: pull species from DB with sqlalchemy, define and implement level algorithm
        species = get_test_species()
        self.__max_hp = species.base_hp
        self.current_hp = self.__max_hp
        self.attack = species.base_attack
        self.speed = species.base_speed
        self.actions = species.actions

    @classmethod
    def from_dict(cls, creature_dict, match=None, board=None):
        if match is not None:
            # get the creature from the match data
            return match.find_creature_in_match(creature_dict["id"])
        else:
            creature = Creature(
                creature_dict["species_id"],
                creature_dict["player_id"],
                creature_dict["level"],
                creature_dict["nickname"],
                id=creature_dict["id"]
            )

            if board is not None and creature_dict["position"] is not None:
                creature.set_position(
                    board[
                        creature_dict["position"]["x"]
                    ]
                    [
                        creature_dict["position"]["y"]
                    ]
                )
            
            return creature

    def set_position(self, new_position):
        # this function's responsibility is to ensure that position.creature_id
        # and creature.position always correspond.

        # handle creature being removed from board

        if new_position is None:
            old_position = self.position
            self.__position = None
            old_position.set_creature_id(None)

        # prevent invalid moves
        
        elif new_position.creature_id is not None and new_position.creature_id != self.id:
            logging.debug("Position is occupied")

        # handle a valid move

        else:
            logging.debug(f"Updating creature {self.nickname} position to [{new_position.x},{new_position.y}]")
            old_position = self.position

            # remove creature from old position
            if old_position is not None:
                old_position.set_creature_id(None)

            # add creature to new position 
            self.__position = new_position
            new_position.set_creature_id(self.id)
            

    def receive_action(self, action):
        # for now, the only type of actions are attacks
        # TODO: add a damage equation that factors in creature defense
        self.current_hp -= action.power
        if self.is_fainted:
            self.remove_from_board()

    def remove_from_board(self):
        if self.position is not None:
            self.set_position(None)

    def find_action_of_creature(self, action_id):
        # TODO: find action by id instead of name
        return next((a for a in self.actions if a.name == action_id), None)
    
    def get_planned_move_path(self, destination):
        board = self.position.board
        path = []
        remaining_speed = self.speed

        def find_path(board, path, current_pos, remaining_speed):
            next_pos = board.get_next_pos_in_path(current_pos, destination)
            if remaining_speed == 0 or next_pos is None:
                return path
            else:
                path.append(next_pos)
                remaining_speed -= 1
                return find_path(board, path, next_pos, remaining_speed)
            
        return find_path(board, path, self.position, remaining_speed)


    def to_simple_dict(self):
        return {
            "id": str(self.id),
            "species_id": str(self.species_id),
            "player_id": str(self.player_id),
            "level": self.level,
            "nickname": self.nickname,
            "max_hp": self.__max_hp,
            "current_hp": self.current_hp,
            "attack": self.attack,
            "speed": self.speed,
            "actions": [a.to_simple_dict() for a in self.actions],
            "position": None if self.position is None else {
                "x": self.position.x,
                "y": self.position.y,
                "creature_id": self.id
            }
        }

def get_test_creature(nickname, player_id=None, id=None):
    return Creature("TEST_CREATURE_SPECIES", player_id, 1, nickname, id=id)