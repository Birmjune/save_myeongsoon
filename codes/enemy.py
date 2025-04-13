from setup import *
from player import Enemy_
from enemy_ import Enemy
from bar import Bar
from pygame.math import Vector2 as vec
from support import *
from bullet import Bullet
from damage import Damage
from tile import BasicWall
import random
from itertools import chain
from math import cos, sin, pi, ceil


class Enemy1(Enemy_):
    def __init__(self, pos):
        super().__init__(pos)
        self.animations = import_files('../graphics/enemy/1', ['stab'])
        self.status = 'stab'
        self.velocity = vec(int(3.5*tile_ratio), 0)
        self.elasticity = 1
        self.damage = Damage(20)

    def update(self, targets=None):
        super().update(targets)


class Enemy2(Enemy_):
    def __init__(self, pos):
        super().__init__(pos)
        self.animations = import_files('../graphics/enemy/2', ['walk', 'attack'])
        self.bullet_imgs = import_files('../graphics/enemy/2/bullets', [None, 'ice', 'fire'], (tile_size//3, tile_size//3))
        self.status = 'walk'
        self.velocity = vec(int(3*tile_ratio), 0)
        self.elasticity = 1
        self.shooting = False
        self.bullet_damages = {None: 10, 'ice': 5, 'fire': 20}
        self.bullet_type = None
        self.effects['shoot_cooltime'] = random.randint(fps//2, fps*1)

    def shoot(self):
        self.shooting = True
        self.effects['shoot_cooltime'] = fps*3//2
        self.bullets.add(Bullet(self.rect.center,
                                self.bullet_imgs[self.bullet_type][0],
                                vec(10*tile_ratio, 0)*(2*self.facing_right-1),
                                self.bullet_damages[self.bullet_type],
                                self.bullet_type))

    def animate(self):
        self.img_idx += self.animate_speed
        if int(self.img_idx) >= len(self.animations[self.status]):
            self.img_idx = 0
            self.status = 'walk'
            self.shooting = False
        img = self.animations[self.status][int(self.img_idx)]
        if self.facing_right:
            self.image = img
        else:
            self.image = transform.flip(img, True, False)
        if self.status == 'attack' and int(self.img_idx) == 2 and not self.shooting:
            self.bullet_type = random.choice([None, 'ice', 'fire'])
            self.shoot()
            self.velocity.x = 0
        elif self.velocity.x == 0:
            self.velocity.x = int(3*tile_ratio)*random.choice([1, -1])

    def update(self, targets=None):
        if self.effects['shoot_cooltime'] == 0:
            self.status = 'attack'
        super().update(targets)


class Enemy3(Enemy_):
    pass


class EnemyMiddle(Enemy, BasicWall):
    def __init__(self, pos):
        Enemy.__init__(self)
        self.size = 16*tile_size
        self.animations = import_files('../graphics/enemy/middleboss', ['stop', 'ready', 'attack'], (self.size, self.size))
        self.bullet_imgs = import_files('../graphics/enemy/middleboss/bullets', [None, 'ice', 'fire'], (tile_size//3, tile_size//3))
        self.status = 'stop'
        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(topleft=tuple(pos))
        self.elasticity = 1
        self.shooting = False
        self.velocity = vec(0, 0)
        self.bullet_damages = {None: 10, 'ice': 5, 'fire': 20}
        self.damage = Damage(0, None)
        self.bullet_type = None
        self.bullet_direction = 0
        self.bullets = sprite.Group()
        self.effects = dict()
        self.effects['prepare_attack'] = 0
        self.health = self.max_health = 1000
        self.health_bar = Bar(self, vec(0, -10), vec(self.size, self.size//30), self.health, self.max_health)

    def shoot(self, direction):
        self.shooting = True
        self.bullets.add(Bullet(self.rect.center,
                                self.bullet_imgs[self.bullet_type][0],
                                vec(round(2*tile_ratio*direction.x), ceil(2*tile_ratio*direction.y)),
                                self.bullet_damages[self.bullet_type],
                                self.bullet_type,
                                knockback=False))

    def attack(self):
        if self.effects['prepare_attack'] == 0:
            self.effects['prepare_attack'] = 6*fps
            self.bullet_direction = random.random()*2*pi

    def encounter_target(self, target):
        if self.rect.colliderect(target.rect):
            target.get_damage(self.damage, None)

    def draw_healthbar(self, screen):
        self.health_bar.get_bar(self.health, bar_color= (255, 63, 63) if 0 < self.health < 0.3*self.max_health else (63, 255, 63))
        if self.health < self.max_health:
            self.health_bar.draw(screen)

    def erase_healthbar(self, screen, bg):
        self.health_bar.get_bar(self.health)
        self.health_bar.erase(screen, bg)

    def die(self):
        self.kill()

    def get_damage(self, damage, damager=None):
        self.health -= damage.num
        if self.health <= 0 or damage.num == 0:
            self.die()
            # self.health = 0
        # if damage.damage_type == ??:

    def effect(self):
        for eff in self.effects.keys():
            self.effects[eff] -= 1
            if self.effects[eff] < 0:
                self.effects[eff] = 0

    def update(self, targets=None):
        if self.health < self.max_health:
            self.attack()
        self.effect()
        if 0 < self.effects['prepare_attack'] <= fps:
            self.status = 'attack'
            if random.random() > 0.5:
                for target in targets:
                    if target is not None:
                        temp_vec = vec(target.rect.center) - vec(self.rect.center)
                        self.shoot(temp_vec/temp_vec.length())
        elif self.effects['prepare_attack'] <= 3*fps:
            self.status = 'ready'
        else:
            self.status = 'stop'
        self.image = self.animations[self.status][0]

        for target in targets:
            if target is not None:
                temp_vec = vec(target.rect.topleft) - vec(self.rect.topleft)
                topleft = self.rect.topleft
                self.rect.topleft = tuple(vec(*self.rect.topleft) + temp_vec/temp_vec.length())
                self.encounter_target(target)
                self.rect.topleft = topleft
        self.image = self.animations[self.status][0]
        barriers = ()
        self.bullets.update(targets, barriers)
        if 0 < self.health < 0.1*self.max_health:
            self.health_bar.bar_color = (255, 63, 63)
        else:
            self.health_bar.bar_color = (63, 255, 63)


class EnemyBoss(Enemy, BasicWall):
    def __init__(self, pos):
        Enemy.__init__(self)
        self.size = 16*tile_size
        self.animations = [import_files(f'../graphics/enemy/boss/{i}', ['stop', 'ready', 'attack'], (self.size, self.size)) for i in range(1, 4)]
        self.bullet_imgs = import_files('../graphics/enemy/boss/bullets', [None, 'ice', 'fire'], (tile_size//3, tile_size//3))
        self.status = 'stop'
        self.phase = 1
        self.image = self.animations[self.phase][self.status][0]
        self.rect = self.image.get_rect(topleft=tuple(pos))
        self.elasticity = 1
        self.shooting = False
        self.velocity = vec(0, 0)
        self.bullet_damages = {None: 10, 'ice': 5, 'fire': 20}
        self.damage = Damage(0, None)
        self.bullet_type = None
        self.bullet_direction = 0
        self.bullets = sprite.Group()
        self.effects = dict()
        self.effects['prepare_attack'] = 0
        self.effects['summon'] = 3*fps
        self.health = self.max_health = 60000
        self.health_bar = Bar(self, vec(0, -10), vec(self.size, self.size//30), self.health, self.max_health)
        self.summoned = sprite.Group()
        self.summon_places = []

    def shoot(self, direction):
        self.shooting = True
        self.bullets.add(Bullet(self.rect.center,
                                self.bullet_imgs[self.bullet_type][0],
                                vec(round(2*tile_ratio*direction.x), ceil(2*tile_ratio*direction.y)),
                                self.bullet_damages[self.bullet_type],
                                self.bullet_type,
                                knockback=False))

    def summon(self, summon_type, pos):
        self.summoned.add(enemy_dict[summon_type](pos))

    def attack(self):
        if self.effects['prepare_attack'] == 0:
            self.effects['prepare_attack'] = 6*fps
        if self.effects['summon'] == 0:
            self.effects['summon'] = 10*fps

    def encounter_target(self, target):
        if self.rect.colliderect(target.rect):
            target.get_damage(self.damage, None)

    def draw_healthbar(self, screen):
        self.health_bar.get_bar(self.health, bar_color= (255, 63, 63) if 0 < self.health < 0.3*self.max_health else (63, 255, 63))
        if self.health < self.max_health:
            self.health_bar.draw(screen)

    def erase_healthbar(self, screen, bg):
        self.health_bar.get_bar(self.health)
        self.health_bar.erase(screen, bg)

    def die(self):
        self.kill()

    def get_damage(self, damage, damager=None):
        self.health -= damage.num
        if self.health <= 0 or damage.num == 0:
            self.die()
            # self.health = 0
        # if damage.damage_type == ??:

    def effect(self):
        for eff in self.effects.keys():
            self.effects[eff] -= 1
            if self.effects[eff] < 0:
                self.effects[eff] = 0

    def update(self, targets=None):
        self.phase = 3-self.health//(self.max_health//3+1)
        self.summoned.empty()
        if self.health < self.max_health:
            self.attack()
        self.effect()
        if self.phase == 1 or self.phase >= 3:
            if 0 < self.effects['prepare_attack'] <= fps:
                self.status = 'attack'
                if random.random() > 0.5:
                    for target in targets:
                        if target is not None:
                            temp_vec = vec(target.rect.center) - vec(self.rect.center)
                            self.shoot(temp_vec/temp_vec.length())
            elif self.effects['prepare_attack'] <= 3*fps:
                self.status = 'ready'
            else:
                self.status = 'stop'
        if self.phase == 2 or self.phase >= 3:
            if self.effects['summon'] == 1*fps:
                self.status = 'stop'
                self.summon(random.choice(['1']), random.choice(self.summon_places))

        for target in targets:
            if target is not None:
                temp_vec = vec(target.rect.topleft) - vec(self.rect.topleft)
                topleft = self.rect.topleft
                self.rect.topleft = tuple(vec(*self.rect.topleft) + temp_vec/temp_vec.length())
                self.encounter_target(target)
                self.rect.topleft = topleft
        self.image = self.animations[self.phase-1][self.status][0]
        barriers = ()
        self.bullets.update(targets, barriers)

enemy_dict = {'1': Enemy1, '2': Enemy2, '3': Enemy3, 'M': EnemyMiddle, 'B': EnemyBoss}
