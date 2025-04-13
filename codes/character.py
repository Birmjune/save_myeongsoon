from pygame import *
from pygame.math import Vector2 as vec
from bar import Bar
from damage import Damage
from setup import *
from tile import *
from itertools import chain


vec0 = vec(0, 0)


class Character(sprite.Sprite):
    def __init__(self, pos):

        super().__init__()

        self.accel = 0
        self.velocity = vec0

        self.gravity = 0 # 0.8*tile_ratio
        self.jump_speed = -16*tile_ratio
        self.jumping = False

        self.animations = dict()
        self.animate_speed = 0.15
        self.img_idx = 0
        self.status = None
        self.facing_right = True

        self.size = vec(tile_size, tile_size)
        self.image = Surface(self.size)
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(topleft=tuple(pos))

        self.on_ground = True
        self.elasticity = 0

        self.health = self.max_health = 100
        self.health_bar = Bar(self, vec(0, -10), vec(tile_size, tile_size//10), self.health, self.max_health)

        self.damage = Damage(10)
        self.enemy_class = None
        self.barrier_class = ()

        self.bullets = sprite.Group()

        self.mass = 1
        self.knockbacked = False
        self.knockback_const = 0.5

        self.attacking = True

        self.can_portal = True

        self.effects = dict()

        self.map = tuple()

        self.effects['stunned'] = 0

    def apply_gravity(self):
        self.velocity.y += self.gravity
        self.rect.y += self.velocity.y
        if self.rect.y > screen_height:
            self.die()

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.velocity.y = self.jump_speed

    def draw_healthbar(self, screen):
        self.health_bar.get_bar(self.health, bar_color=(255, 63, 63) if 0 < self.health < 0.3*self.max_health else (63, 255, 63))
        if self.health < self.max_health:
            self.health_bar.draw(screen)

    def erase_healthbar(self, screen, bg):
        self.health_bar.get_bar(self.health)
        self.health_bar.erase(screen, bg)

    def get_damage(self, damage, damager=None):
        if damage.num is None:
            self.die()
            return
        self.health -= damage.num
        if damager is not None:
            self.knockback(damager.velocity.x)
        if self.health <= 0:
            self.die()
            # self.health = 0
        # if damage.damage_type == ??:

    def knockback(self, vel_x=None):
        if vel_x is None:
            vel_x = -self.velocity.x
        if vel_x == 0:
            return
        self.knockbacked = True
        rect_ = self.rect.copy()
        rect_.topleft += vec(self.knockback_const*tile_size*(vel_x/abs(vel_x)), 0)
        touched = False
        for spr in self.map:
            if spr.rect.colliderect(rect_):
                if any(isinstance(spr, barc) for barc in self.barrier_class):
                    if vel_x > 0:
                        rect_.right = spr.rect.left
                    elif vel_x < 0:
                        rect_.left = spr.rect.right
        #             touched = True
        # if touched:
        #     pass
            # self.velocity.x *= -self.elasticity
        if rect_.x < 0:
            rect_.x = 0
        elif rect_.x > screen_width - self.size.x:
            rect_.x = screen_width - self.size.x

        self.rect.topleft = rect_.topleft

    def hor_collisions(self):
        touched = False
        if not self.effects['stunned']:
            self.rect.x += self.velocity.x
        for spr in self.map:
            if spr.rect.colliderect(self.rect):
                if any(isinstance(spr, barc) for barc in self.barrier_class):
                    if self.velocity.x > 0:
                        self.rect.right = spr.rect.left
                    elif self.velocity.x < 0:
                        self.rect.left = spr.rect.right
                    touched = True
        if touched:
            self.velocity.x *= -self.elasticity

    def ver_collisions(self):
        self.apply_gravity()
        grvt = 0.8*tile_ratio
        can_portal = True
        tbd = False # to be damaged
        damaging_sprs = []
        for spr in self.map:
            if spr.rect.colliderect(self.rect):
                if any(isinstance(spr, barc) for barc in self.barrier_class):
                    if self.velocity.y > 0:
                        self.rect.bottom = spr.rect.top
                        self.jumping = False
                    elif self.velocity.y < 0:
                        self.rect.top = spr.rect.bottom
                    self.velocity.y = 0
                elif isinstance(spr, Spike):
                    tbd = True
                    damaging_sprs.append(spr)
                if isinstance(spr, Up):
                    grvt = min(grvt, -1.6)
                elif isinstance(spr, Down):
                    grvt = max(grvt, 1.6)
                if isinstance(spr, Portal) and spr.out_pos():
                    if self.can_portal:
                        self.rect.topleft = spr.out_pos()
                        self.velocity.y = 0

        if tbd:
            for spr in damaging_sprs:
                if isinstance(spr, Spike) and spr.rect.colliderect(self.rect):
                    self.get_damage(Damage(100, None))
        self.can_portal = can_portal
        self.gravity = grvt

    def hor_out_of_range(self):
        if self.rect.x < 0:
            self.rect.x = 0
            self.velocity.x *= -self.elasticity
        elif self.rect.x > screen_width - self.size.x:
            self.rect.x = screen_width - self.size.x
            self.velocity.x *= -self.elasticity

    def ver_out_of_range(self):
        if self.rect.y < tile_size:
            self.rect.y = tile_size
            self.velocity.y *= -self.elasticity

    def animate(self):
        self.img_idx += self.animate_speed
        if int(self.img_idx) >= len(self.animations[self.status]):
            self.img_idx = 0
        img = self.animations[self.status][int(self.img_idx)]
        if self.facing_right:
            self.image = img
        else:
            self.image = transform.flip(img, True, False)

    def encounter_target(self, target):
        if self.rect.colliderect(target.rect):
            if self.velocity.x*(self.velocity.x-target.velocity.x) > 0 and self.attacking:
                target.get_damage(self.damage, self)
            self.knockback()

    def encounter_barrier(self, barriers):
        if self.rect.colliderect(barriers.rect):
            self.knockback()

    def die(self):
        self.kill()

    def stun(self, stun_time=0.5):
        self.effects['stunned'] = int(stun_time)

    def effect(self):
        for eff in self.effects.keys():
            self.effects[eff] -= 1
            if self.effects[eff] < 0:
                self.effects[eff] = 0

    def update(self, targets):
        self.effect()
        self.hor_collisions()
        self.ver_collisions()
        self.hor_out_of_range()
        self.ver_out_of_range()
        for target in targets:
            if target is not None:
                self.encounter_target(target)
        self.animate()
        barriers = [*tuple(spr for spr in self.map if any(isinstance(spr, barc) for barc in self.barrier_class))]
        # barriers = ()
        self.bullets.update(targets, barriers)
