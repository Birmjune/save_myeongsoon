from pygame import *
from support import import_files
from setup import *


class Weapon(sprite.Sprite):
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

    def attack(self, speed=None):
        pass

    def animate(self):

        self.img_idx += self.animate_speed
        if int(self.img_idx) >= len(self.animations):
            self.img_idx = 0

        self.image = self.animations[self.status][int(self.img_idx)]

    def update(self):
        self.animate()
        self.set_rect()


# class Sword(Weapon):
#     def __init__(self, character, sword_type=1):
#
#         super().__init__(character)
#
#         self.animations = import_files(f'../graphics/weapon/sword{sword_type}', ['stop'], (self.weapon_size, self.weapon_size))
#
#         self.image_real = self.animations[self.status][self.img_idx]
#         self.image = self.image_real
#         self.rect = self.image.get_rect()
#
#         self.slashing = 0
#         self.slashing_speed = 1
#         self.slash_angle = 90
#
#     def attack(self, speed=None):
#         if speed is not None:
#             self.slashing_speed = speed
#         self.slashing = self.slash_angle
#
#     def animate(self):
#         if self.slashing > 0:
#             self.slashing -= self.slashing_speed
#             img = transform.rotate(self.image_real, -(self.slash_angle-self.slashing))
#             self.owner.attacking = True
#         else:
#             img = self.image_real
#             self.owner.attacking = False
#
#         if self.owner.facing_right:
#             self.image = img
#         else:
#             self.image = transform.flip(img, True, False)
#
#     def __del__(self):
#         self.owner.attacking = False


class Gun(Weapon):
    def __init__(self, character, sword_type=1):

        super().__init__(character)

        self.animations = import_files(f'../graphics/weapon/sword{sword_type}', ['stop'], (self.weapon_size, self.weapon_size))

        self.image_real = self.animations[self.status][self.img_idx]
        self.image = self.image_real
        self.rect = self.image.get_rect()

    def attack(self, speed=None):
        self.owner.shoot()

    def animate(self):
        img = self.image_real

        if self.owner.facing_right:
            self.image = img
        else:
            self.image = transform.flip(img, True, False)


class Shield(Weapon):
    def __init__(self, character):
        super().__init__(character)
        self.weapon_size = int(1.5*tile_size)
        self.animations = import_files('../graphics/weapon/shield', ['stop'], (self.weapon_size, self.weapon_size))
        self.image_real = self.animations[self.status][self.img_idx]
        self.rect = self.image_real.get_rect()

    def set_rect(self):
        self.rect.center = self.owner.rect.center

    def animate(self):
        if self.owner.effects['shield']:
            self.image = self.image_real
        else:
            self.image = Surface((0, 0))
