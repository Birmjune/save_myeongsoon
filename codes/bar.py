from pygame import *
from pygame.math import Vector2 as vec


class Bar_(sprite.Sprite):
    def __init__(self, pos, size, bar_color):
        super().__init__()
        self.image = Surface(tuple(size))
        self.image.fill(bar_color)
        self.rect = self.image.get_rect(center=tuple(pos))

    def update(self, pos, size, bar_color):
        self.image = Surface(tuple(size))
        self.image.fill(bar_color)
        self.rect = self.image.get_rect(center=tuple(pos))


class Bar:
    def __init__(self, spr, pos, size, value, max_value, bar_color=(63, 255, 63), delta=1):

        self.bars = sprite.Group()

        center_pos = vec(spr.rect.centerx, spr.rect.top) + pos
        bar1_pos = center_pos - vec((size.x*(1 - value/max_value))/2, 0)
        bar2_pos = center_pos + vec((size.x*(value/max_value))/2, 0)

        self.bar1 = Bar_(bar1_pos, (size.x*value/max_value, size.y), bar_color)
        self.bar2 = Bar_(bar2_pos, (size.x*(1-value/max_value), size.y), (0, 0, 0))
        self.bar3 = Bar_(center_pos, size+2*vec(delta, delta), (255, 255, 255))

        self.bars.add(self.bar3)
        self.bars.add(self.bar1)
        self.bars.add(self.bar2)

        self.sprite = spr
        self.max_value = max_value
        self.value = value
        self.size = size
        self.pos = pos
        self.delta = delta
        self.bar_color = bar_color

    def get_bar(self, value, bar_color=None):
        if bar_color is not None:
            self.bar_color = bar_color
        center_pos = vec(self.sprite.rect.centerx, self.sprite.rect.top) + self.pos
        bar1_pos = center_pos - vec((self.size.x*(1 - value/self.max_value))/2, 0)
        bar2_pos = center_pos + vec((self.size.x*(value/self.max_value))/2, 0)
        self.bar1.update(bar1_pos, (self.size.x*value/self.max_value, self.size.y), self.bar_color)
        self.bar2.update(bar2_pos, (self.size.x*(1-value/self.max_value), self.size.y), (0, 0, 0))
        self.bar3.update(center_pos, self.size+2*vec(self.delta, self.delta), (255, 255, 255))

    def draw(self, screen):
        self.bars.draw(screen)

    def erase(self, screen, bg):
        self.bars.clear(screen, bg)
