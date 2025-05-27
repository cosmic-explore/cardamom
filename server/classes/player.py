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
    
    def to_simple_dict(self):
        """For the JSON serialization of Player objects."""
        return {
            "id": str(self.id),
            "name": self.name,
            "creatures": [c.to_simple_dict() for c in self.creatures]
        }
    
def get_test_player_1():
    player = Player("Safari", id="TEST_USER_1")
    player.creatures.append(get_test_creature("A", player_id=player.id, id="test_creature_1"))
    return player

def get_test_player_2():
    player = Player("Firehawk", id="TEST_USER_2")
    player.creatures.append(get_test_creature("B", player_id=player.id, id="test_creature_2"))
    return player
