class Action:
    def __init__(self, name, speed, power):
        self.name = name
        self.speed = speed
        self.power = power

def get_test_attack():
    return Action("test attack", 1, 1)