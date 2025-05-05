from.action import get_test_attack

class Species:
    
    def __init__(self, name, base_attack, base_hp, base_speed):
        self.name = name
        self.base_attack = base_attack,
        self.base_hp = base_hp
        self.base_speed = base_speed
        self.actions = [get_test_attack()]

def get_test_species():
    return Species("Test Species", 1, 1, 4)