class Player:
    def __init__(self, name):
        self.name = name
        self.creatures = []

    def get_user_id(self):
        """Func required by oauth"""
        return self.id