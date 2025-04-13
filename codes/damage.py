class Damage:
    def __init__(self, num, damage_type=None):
        self.num = num
        self.damage_type = damage_type

    def __tuple__(self):
        return self.num, self.damage_type

    def __mul__(self, num):
        return Damage(self.num*num, self.damage_type)
