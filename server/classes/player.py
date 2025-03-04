from uuid import uuid4
from .creature import get_test_creature

class Player:
    def __init__(self, name, id=None):
        self.id = id if id is not None else uuid4()
        self.name = name
        self.creatures = []

    def get_user_id(self):
        """Func required by oauth"""
        return self.id
    
def get_test_player_1():
    player = Player("Safari")
    player.creatures.append(get_test_creature("A"))
    return player

def get_test_player_2():
    player = Player("Firehawk")
    player.creatures.append(get_test_creature("B"))
    return player