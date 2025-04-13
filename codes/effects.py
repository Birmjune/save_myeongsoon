from pygame import *
from support import import_files
from setup import *


class Effect(sprite.Sprite):
    def __init__(self, character):

        super().__init__()

        self.owner = character

        self.animations = dict()
        self.animate_speed = 0.15
        self.img_idx = 0
        self.status = 'stop'

        self.weapon_size = tile_size//2

    def set_rect(self):
        self.rect.center = (self.owner.rect.right if self.owner.facing_right else self.owner.rect.left, self.owner.rect.centery)

    def animate(self):
        pass

    def update(self):
        self.animate()
        self.set_rect()


class ShieldEffect(Effect):
    def __init__(self, character):
        super().__init__(character)
        self.weapon_size = int(1.5*tile_size)
        self.animations = import_files('../graphics/effect/shield', ['stop'], (self.weapon_size, self.weapon_size))
        self.image_real = self.animations[self.status][self.img_idx]
        self.rect = self.image_real.get_rect()

    def set_rect(self):
        self.rect.center = self.owner.rect.center

    def animate(self):
        if self.owner.effects['shield']:
            self.image = self.image_real
        else:
            self.image = Surface((0, 0))


class AtkBoostEffect(Effect):
    def __init__(self, character):
        super().__init__(character)
        self.weapon_size = int(1.5*tile_size)
        self.animations = import_files('../graphics/effect/atkboost', ['stop'], (self.weapon_size, self.weapon_size))
        self.image_real = self.animations[self.status][self.img_idx]
        self.rect = self.image_real.get_rect()

    def set_rect(self):
        self.rect.center = self.owner.rect.center

    def animate(self):
        if self.owner.effects['atk_boost']:
            self.image = self.image_real
        else:
            self.image = Surface((0, 0))


class AtkSpeedBoostEffect(Effect):
    def __init__(self, character):
        super().__init__(character)
        self.weapon_size = int(1.5*tile_size)
        self.animations = import_files('../graphics/effect/atkspeedboost', ['stop'], (self.weapon_size, self.weapon_size))
        self.image_real = self.animations[self.status][self.img_idx]
        self.rect = self.image_real.get_rect()

    def set_rect(self):
        self.rect.center = self.owner.rect.center

    def animate(self):
        if self.owner.effects['atk_speed_boost']:
            self.image = self.image_real
        else:
            self.image = Surface((0, 0))
