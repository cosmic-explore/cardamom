from .species import get_test_species

class Creature:
    
    def __init__(self, species_id, player_id, level, nickname):
        self.species_id = species_id
        self.player_id = player_id
        self.level = level
        self.nickname = nickname
        self.__init_from_species(species_id, level)
        
        self.__position = None

    @property
    def position(self):
        return self.__position

    def __init_from_species(self, species_id, level):
        # TODO: pull species from DB
        species = get_test_species()
        self.current_hp = species.base_hp
        self.attack = species.base_attack
        self.speed = species.base_speed

    def set_position(self, new_position):
        # it's this function's responsibility to ensure that position.creature
        # and creature.position always correspond.

        if self.position is new_position:
            return

        if new_position.creature is not None and new_position.creature is not self:
            print("Space is occupied")
        else:
            old_position = self.position
            self.__position = new_position
            
            if old_position is not None:
                old_position.set_creature(None)
            
            if new_position.creature is not self:
                new_position.set_creature(self)
    