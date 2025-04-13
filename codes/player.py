from pygame import *
from setup import *
from support import *
from bar import Bar
from tile import *
from item import *
from pygame.math import Vector2
from damage import Damage
from character import Character
from enemy_ import Enemy
from bullet import Bullet
from effects import *
from itertools import chain
import time as t
from end_check import *
from sounds import jump_sound, die_sound


player_status = [None]


class Player(Character):
    def __init__(self, pos, status=None):
        super().__init__(pos)
        self.max_velocity = 10*tile_ratio
        self.accel = 1*tile_ratio
        self.enemy_class = (Enemy,)
        self.barrier_class = (BasicWall,)
        self.animations = import_files('../graphics/player', ['stop', 'attack'])
        self.status = 'stop'
        self.attacking = False

        self.bullet_imgs = import_files('../graphics/player/bullets', [None], (tile_size//3, tile_size//3))
        self.shooting = False
        self.bullet_type = None
        self.effects['shoot_cooltime'] = 0

        self.special_bullets = sprite.Group()

        self.damage_ = Damage(18, None)
        self.item = sprite.GroupSingle()

        if status is None:
            max_health = (1 if game_mode[0] == 'crazy' else 100)
            status = (max_health, max_health, 0)
        self.health, self.max_health, self.special_attack_gauge = status

        self.health_bar = Bar(self, vec(0, -20), vec(tile_size, tile_size//10), self.health, self.max_health)

        self.effects['stopping_enemies'] = 0

        self.animate_speed = 0.05

        self.special_effect = sprite.GroupSingle()
        self.effects['shield'] = 0
        self.effects['atk_boost'] = 0
        self.effects['atk_speed_boost'] = 0

        self.max_special_attack_gauge = 1000
        self.special_attack_gauge_bar = Bar(self, vec(0, -10), vec(tile_size, tile_size//10), self.special_attack_gauge, self.max_special_attack_gauge, bar_color=(63, 255, 255))
        self.effects['special_attack'] = 0

    def get_input(self):
        keys = key.get_pressed()

        if keys[K_RIGHT] or keys[K_d]:
            self.velocity.x += self.accel
            self.facing_right = True
        elif keys[K_LEFT] or keys[K_a]:
            self.velocity.x -= self.accel
            self.facing_right = False
        else:
            if abs(self.velocity.x) > self.accel/2:
                self.velocity.x -= self.velocity.x / abs(self.velocity.x) * self.accel
            else:
                self.velocity.x = 0
        if abs(self.velocity.x) > self.max_velocity:
            self.velocity.x *= self.max_velocity / abs(self.velocity.x)

        if keys[K_UP] or keys[K_w]:
            self.jump()

        if keys[K_SPACE]:
            self.use_item()

        if keys[K_f]:
            self.shoot()

        if keys[K_s]:
            if self.special_attack_gauge == self.max_special_attack_gauge:
                self.effects['special_attack'] = int(0.5*fps)
                self.special_attack_gauge = 0

        if keys[K_l]:
            self.die()

        if game_mode[0] == 'manager':
            if keys[K_q]:
                if self.health > 0:
                    self.get_damage(Damage(1), None)
            elif keys[K_e]:
                if self.health < self.max_health:
                    self.health += 1

            if keys[K_SEMICOLON]:
                self.jumping = False

            if keys[K_k]:
                self.effects['shield'] = 6*fps

            if keys[K_SLASH]:
                end_level()
                t.sleep(0.5)

            if keys[K_PERIOD]:
                self.item.sprite = random_item()()
                t.sleep(0.5)

            if keys[K_p]:
                self.special_attack_gauge += 10
                if self.special_attack_gauge > self.max_special_attack_gauge:
                    self.special_attack_gauge = self.max_special_attack_gauge

    def ver_collisions(self):
        self.apply_gravity()
        grvt = 0.8*tile_ratio
        tbd = True
        damaging_sprs = []
        can_portal = True
        for spr in self.map:
            if spr.rect.colliderect(self.rect):
                if any(isinstance(spr, barc) for barc in self.barrier_class):
                    if self.velocity.y > 0:
                        self.rect.bottom = spr.rect.top
                        self.jumping = False
                    elif self.velocity.y < 0:
                        self.rect.top = spr.rect.bottom
                    self.velocity.y = 0
                if isinstance(spr, Up):
                    grvt = min(grvt, -1.6)
                elif isinstance(spr, Down):
                    grvt = max(grvt, 1.6)
                if isinstance(spr, Portal) and spr.out_pos():
                    if self.can_portal:
                        self.rect.topleft = spr.out_pos()
                        self.velocity.y = 0
                if isinstance(spr, Spike):
                    tbd = True
                    damaging_sprs.append(spr)
                if isinstance(spr, ExitPortal):
                    if not any(any(isinstance(spr, enm) for enm in self.enemy_class) for spr in self.map):
                        player_status[0] = (self.health, self.max_health, self.special_attack_gauge)
                        end_level()
                if isinstance(spr, ItemBox):
                    self.item.add(spr.get_item())
        if tbd:
            for spr in damaging_sprs:
                if isinstance(spr, Spike) and spr.rect.colliderect(self.rect):
                    self.get_damage(Damage(None, None))
        self.can_portal = can_portal
        self.gravity = grvt

    def die(self):
        self.health = 0
        # self.kill()
        end_game()

    def shoot(self):
        if self.effects['shoot_cooltime'] == 0:
            self.status = 'attack'
            self.shooting = True
            self.bullets.add(Bullet(self.rect.center,
                                    self.bullet_imgs[self.bullet_type][0],
                                    vec(10*tile_ratio, 0)*(2*self.facing_right-1),
                                    self.damage.num,
                                    self.bullet_type,
                                    shooter=self))
            self.effects['shoot_cooltime'] = int((player_atk_delay*fps)*(1-0.5*bool(self.effects['atk_speed_boost'])))

    def special_attack(self):
        if (self.effects['special_attack']+1)%3==0:
            theta = pi*(2*random.random()-1)/12 + pi*int(not self.facing_right)
            self.special_bullets.add(Bullet(self.rect.center,
                                            self.bullet_imgs[self.bullet_type][0],
                                            vec(int(10 * tile_ratio * cos(theta)), int(10 * tile_ratio * sin(theta))),
                                            self.damage.num,
                                            self.bullet_type,
                                            knockback=False))

    def draw_gauge(self, screen):
        self.special_attack_gauge_bar.get_bar(self.special_attack_gauge, bar_color=(63, 63, 255) if self.special_attack_gauge == self.max_special_attack_gauge else (255, 127, 127))
        if self.special_attack_gauge > 0:
            self.special_attack_gauge_bar.draw(screen)

    def erase_gauge(self, screen, bg):
        self.special_attack_gauge_bar.get_bar(self.health)
        self.special_attack_gauge_bar.erase(screen, bg)

    def get_damage(self, damage, damager=None):
        damage_num = damage.num
        if self.effects['shield'] and damage_num is not None:
            damage_num *= 0
        if not self.effects['shield']:
            super().get_damage(Damage(damage_num, damage.damage_type), damager)

    def use_item(self):
        if isinstance(self.item.sprite, Heal):
            self.health += 100
            if self.health > self.max_health:
                self.health = self.max_health
        if isinstance(self.item.sprite, Stop):
            self.effects['stopping_enemies'] = 5*fps
        if isinstance(self.item.sprite, Defend):
            self.special_effect.sprite = ShieldEffect(self)
            self.effects['shield'] = 6 * fps
        if isinstance(self.item.sprite, AtkBoost):
            self.special_effect.sprite = AtkBoostEffect(self)
            self.effects['atk_boost'] = 6*fps
        if isinstance(self.item.sprite, AtkSpeedBoost):
            self.special_effect.sprite = AtkSpeedBoostEffect(self)
            self.effects['atk_speed_boost'] = 6*fps
        if isinstance(self.item.sprite, UltimateCharge):
            self.special_attack_gauge = self.max_special_attack_gauge
        if isinstance(self.item.sprite, LivePlusOne):
            live_plus_1[0] = True
        self.item.empty()

    def animate(self):
        self.img_idx += self.animate_speed
        if int(self.img_idx) >= len(self.animations[self.status]):
            self.img_idx = 0
            self.status = 'stop'
        img = self.animations[self.status][int(self.img_idx)]
        if self.facing_right:
            self.image = img
        else:
            self.image = transform.flip(img, True, False)

    def update(self, targets=None):
        if self.effects['atk_boost']:
            self.damage = self.damage_*4
        else:
            self.damage = self.damage_
        self.get_input()
        self.special_effect.update()

        super().update(targets)

        self.special_attack_gauge += 0.1
        if self.special_attack_gauge > self.max_special_attack_gauge:
            self.special_attack_gauge = self.max_special_attack_gauge
        self.special_attack()
        barriers = ()
        self.special_bullets.update(targets, barriers)


class Enemy_(Character, Enemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.image.fill((0, 255, 255))
        self.enemy_class = (Player,)
        self.velocity = vec(5*tile_size, 0)
        self.barrier_class = (BasicWall, Enemy, Spike)
        self.direction = 1
        self.gravity *= 5

    # def ver_collisions(self):
    #     self.apply_gravity()
    #     grvt = 0.8*tile_ratio
    #     can_portal = True
    #     tbd = False # to be damaged
    #     damaging_sprs = []
    #     # on_ground = False
    #     for spr in self.map:
    #         if spr.rect.colliderect(self.rect):
    #             if any(isinstance(spr, barc) for barc in self.barrier_class):
    #                 if self.velocity.y > 0:
    #                     self.rect.bottom = spr.rect.top
    #                     self.jumping = False
    #                 elif self.velocity.y < 0:
    #                     self.rect.top = spr.rect.bottom
    #                 self.velocity.y = 0
    #                 # on_ground = True
    #             if isinstance(spr, Up):
    #                 grvt = min(grvt, -1.6)
    #             elif isinstance(spr, Down):
    #                 grvt = max(grvt, 1.6)
    #             if isinstance(spr, Portal) and spr.out_pos():
    #                 if self.can_portal:
    #                     self.rect.topleft = spr.out_pos()
    #                     self.velocity.y = 0
    #             if isinstance(spr, Spike):
    #                 tbd = True
    #                 damaging_sprs.append(spr)
    #         # if self.velocity.y > 0 and (not (spr.rect.colliderect(self.rect) and any(isinstance(spr, barc) for barc in self.barrier_class))):
    #         #     on_ground = True
    #
    #     if tbd:
    #         for spr in damaging_sprs:
    #             if isinstance(spr, Spike) and spr.rect.colliderect(self.rect):
    #                 self.velocity.x *= -1
    #     # if not on_ground:
    #     #     print('2')
    #     #     self.velocity.x *= -1
    #         # self.velocity += vec(0, -self.gravity*2)
    #     self.can_portal = can_portal
    #     self.gravity = grvt

    def update(self, targets=None):
        self.effect()
        self.ver_collisions()
        self.hor_collisions()
        self.hor_out_of_range()
        self.ver_out_of_range()
        if self.velocity.x < 0:
            self.facing_right = False
        elif self.velocity.x > 0:
            self.facing_right = True
        for target in targets:
            if target is not None:
                self.encounter_target(target)
        self.animate()
        barriers = [*tuple(spr for spr in self.map if any(isinstance(spr, barc) for barc in self.barrier_class if barc != Spike))]
        self.bullets.update(targets, barriers)
