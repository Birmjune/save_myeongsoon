from character import Character


class Princess(Character):
    def __init__(self, pos):
        super().__init__(pos)
        self.wall_type = 'exit portal'
