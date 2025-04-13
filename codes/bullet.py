from pygame import *
from setup import *
from damage import Damage


class Bullet(sprite.Sprite):
    def __init__(self, pos, img, vel, bullet_damage, bullet_type=None, knockback=True, shooter=None):
        super().__init__()
        self.image = img
        self.velocity = vel
        self.rect = self.image.get_rect(center=pos)
        self.bullet_type = bullet_type
        self.damage = Damage(bullet_damage, bullet_type)
        self.knockback = knockback
        self.shooter = shooter

    def out(self):
        return not (0 <= self.rect.x <= screen_width and 0 <= self.rect.y <= screen_height)

    def update(self, targets, barriers):
        self.rect.topleft += self.velocity
        for target in targets:
            if self.rect.colliderect(target.rect):
                target.get_damage(self.damage, self if self.knockback else None)
                self.kill()
                try:
                    self.shooter.special_attack_gauge += 10
                    if self.shooter.special_attack_gauge > self.shooter.max_special_attack_gauge:
                        self.shooter.special_attack_gauge = self.shooter.max_special_attack_gauge

                except AttributeError:
                    pass
        if self.out() or any(self.rect.colliderect(barrier) for barrier in barriers):
            self.kill()
