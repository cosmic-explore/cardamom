from uuid import uuid4
from .species import get_test_species

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

    def set_position(self, new_position):
        # it's this function's responsibility to ensure that position.creature
        # and creature.position always correspond.

        if self.position is new_position:
            return
        elif new_position is None:
            old_position = self.position
            self.__position = None
            old_position.set_creature(None)
        elif new_position.creature is not None and new_position.creature is not self:
            print("Space is occupied")
        else:
            old_position = self.position
            self.__position = new_position
            
            if old_position is not None:
                old_position.set_creature(None)
            
            if new_position.creature is not self:
                new_position.set_creature(self)

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
                "y": self.position.y
            }
        }

def get_test_creature(nickname):
    return Creature(None, None, 1, nickname)