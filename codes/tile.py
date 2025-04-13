from pygame import *
from support import *
from damage import Damage
from bullet import Bullet
import random
from math import pi, cos, sin
from enemy_ import Enemy


class Tile(sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = Surface((size, size))
        self.animate_speed = 0.15
        self.rect = self.image.get_rect(topleft=tuple(pos))
        # if wall_type == 'basic':
        #     wall_color = (127, 127, 127)
        # elif wall_type == 'exit portal':
        #     wall_color = (0, 127, 127)
        # elif wall_type == 'up':
        #     wall_color = (255, 255, 127)
        # elif wall_type == 'down':
        #     wall_color = (255, 127, 255)
        # elif wall_type == 'portalin0':
        #     wall_color = (127, 255, 255)
        # elif wall_type == 'portalout0':
        #     wall_color = (255, 127, 127)
        # elif wall_type == 'spike':
        #     self.image = Surface((size, size-1))
        #     wall_color = (127, 255, 127)
        # elif wall_type == 'item':
        #     wall_color = (155, 109, 79)
        # self.image.fill(wall_color)
        # self.rect = self.image.get_rect(topleft=tuple(pos))

    def animate(self, *args):
        pass

    def update(self, *args):
        self.animate(*args)


class SummonPlace(Tile):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.image = import_files('../graphics/tiles/summon_place', ['stop'])['stop'][0]


class BasicWall(Tile):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.image.fill((50, 50, 50))


class Spike(sprite.Sprite):
    pass


class SpikeDown(Spike):
    def __init__(self, pos, size):
        super().__init__()
        self.image = import_files('../graphics/tiles/spike', ['down'], (size, int(size*12/26)))['down'][0]
        self.rect = self.image.get_rect(topleft=pos)


class SpikeUp(Spike):
    def __init__(self, pos, size):
        super().__init__()
        self.image = import_files('../graphics/tiles/spike', ['up'], (size, int(size*12/26)))['up'][0]
        self.rect = self.image.get_rect(bottomleft=pos+vec(0, tile_size))


class SpikeLeft(Spike):
    def __init__(self, pos, size):
        super().__init__()
        self.image = import_files('../graphics/tiles/spike', ['left'], (int(size*12/26), size))['left'][0]
        self.rect = self.image.get_rect(topright=pos+vec(tile_size, 0))


class SpikeRight(Spike):
    def __init__(self, pos, size):
        super().__init__()
        self.image = import_files('../graphics/tiles/spike', ['right'], (int(size*12/26), size))['right'][0]
        self.rect = self.image.get_rect(topleft=pos)


class Up(Tile):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.animate_speed = 0.015
        self.animations = import_files('../graphics/tiles/up', ['stop'])
        self.status = 'stop'
        self.img_idx = 0
        self.image = self.animations[self.status][self.img_idx]

    def animate(self, *args):
        self.img_idx += self.animate_speed
        if int(self.img_idx) >= len(self.animations[self.status]):
            self.img_idx = 0
        self.image = self.animations[self.status][int(self.img_idx)]


class Down(Tile):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.animate_speed = 0.015
        self.animations = import_files('../graphics/tiles/down', ['stop'])
        self.status = 'stop'
        self.img_idx = 0
        self.image = self.animations[self.status][self.img_idx]

    def animate(self, *args):
        self.img_idx += self.animate_speed
        if int(self.img_idx) >= len(self.animations[self.status]):
            self.img_idx = 0
        self.image = self.animations[self.status][int(self.img_idx)]


class Portal(Tile):
    def __init__(self, pos, size, out_pos=None, portal_num=0):
        self.portal_num = portal_num
        super().__init__(pos, size)
        tmp = import_files(f'../graphics/tiles/portals/portal{"in" if out_pos else "out"}/{portal_num}', ['stop'])
        self.image = tmp['stop'][portal_num]
        self.out_position = out_pos

    def out_pos(self):
        return self.out_position


class ItemBox(Tile):
    def __init__(self, pos, size, item):
        super().__init__(pos, size)
        self.animations = import_files('../graphics/tiles/treasurechest', ['stop', 'open'])
        self.status = 'stop'
        self.image = self.animations[self.status][0]
        self.item = item

    def get_item(self):
        # self.status = 'open'
        # self.image = self.animations[self.status][0]
        self.kill()
        return self.item


class ExitPortal(Tile):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.animations = import_files('../graphics/tiles/exitportal', ['stop', 'open'])
        self.status = 'stop'
        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(topleft=tuple(pos))

    def animate(self, opened):
        self.status = 'stop' if not opened else 'open'
        self.image = self.animations[self.status][0]


class Princess(ExitPortal):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.animations = import_files('../graphics/princess', ['stop'])
        self.image = self.animations['stop'][0]


class Shooter(BasicWall):
    def __init__(self, pos, size, direction):
        super(Shooter, self).__init__(pos, size)
        self.size = tile_size
        self.animations = import_files('../graphics/tiles/basic_wall', ['stop'], (self.size, self.size))
        self.bullet_imgs = import_files('../graphics/tiles/shooter_bullets', [None, 'ice', 'fire'], (tile_size//3, tile_size//3))
        self.status = 'stop'
        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(topleft=tuple(pos))
        self.bullet_damages = {None: 10, 'ice': 5, 'fire': 20}
        self.damage = Damage(0, None)
        self.bullet_type = None
        self.bullet_direction = direction
        self.bullets = sprite.Group()
        self.effects = dict()
        self.effects['prepare_attack'] = 0
        self.attack_range = 2*tile_size
        self.map = tuple()
        self.barrier_class = (Enemy,)

    def shoot(self):
        self.bullets.add(Bullet(self.rect.center,
                                self.bullet_imgs[self.bullet_type][0],
                                int(2*tile_ratio)*self.bullet_direction,
                                self.bullet_damages[self.bullet_type],
                                self.bullet_type,
                                knockback=False))

    def attack(self):
        if self.effects['prepare_attack'] == 0:
            self.effects['prepare_attack'] = int(1*fps)
            # self.bullet_direction = random.random()*2*pi

    def effect(self):
        for eff in self.effects.keys():
            self.effects[eff] -= 1
            if self.effects[eff] < 0:
                self.effects[eff] = 0

    def draw_healthbar(self, screen):
        pass

    def erase_healthbar(self, screen, background):
        pass

    def get_damage(self, *args):
        pass

    def update(self, targets=None):
        if any(abs(target.rect.y-self.rect.y) < self.attack_range for target in targets):
            self.attack()
        self.effect()
        if 0 < self.effects['prepare_attack'] <= 0.5*fps:
            self.status = 'attack'
            if random.random() > 0.9:
                self.shoot()
        elif 0.5*fps < self.effects['prepare_attack'] <= 1*fps:
            self.status = 'ready'
        else:
            self.status = 'stop'
        self.image = self.animations[self.status][0]
        self.image = self.animations[self.status][0]
        barriers = [*tuple(spr for spr in self.map if any(isinstance(spr, barc) for barc in self.barrier_class))]
        self.bullets.update(targets, barriers)


class ShooterLeft(Shooter):
    def __init__(self, pos, size):
        super().__init__(pos, size, vec(-1, 0))
        self.animations = import_files('../graphics/tiles/shooter_left', ['stop', 'ready', 'attack'], (self.size, self.size))


class ShooterRight(Shooter):
    def __init__(self, pos, size):
        super().__init__(pos, size, vec(1, 0))
        self.animations = import_files('../graphics/tiles/shooter_right', ['stop', 'ready', 'attack'], (self.size, self.size))
