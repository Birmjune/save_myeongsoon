from pygame import *
from setup import *
import random
from support import *


class Item(sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = Surface((0, 0))
        self.rect = self.image.get_rect(topright=(screen_width, 0))


class Heal(Item):
    def __init__(self):
        super().__init__()
        self.image = import_files('../graphics/items', ['heal'], size=(tile_size*2, tile_size*2))['heal'][0]
        self.rect = self.image.get_rect(topright=(screen_width, 0))


class Stop(Item):
    def __init__(self):
        super().__init__()
        self.image = import_files('../graphics/items', ['stop'], size=(tile_size*2, tile_size*2))['stop'][0]
        self.rect = self.image.get_rect(topright=(screen_width, 0))


class Defend(Item):
    def __init__(self):
        super().__init__()
        self.image = import_files('../graphics/items', ['shield'], size=(tile_size*2, tile_size*2))['shield'][0]
        self.rect = self.image.get_rect(topright=(screen_width, 0))


class AtkBoost(Item):
    def __init__(self):
        super().__init__()
        self.image = import_files('../graphics/items', ['atkboost'], size=(tile_size*2, tile_size*2))['atkboost'][0]
        self.rect = self.image.get_rect(topright=(screen_width, 0))


class AtkSpeedBoost(Item):
    def __init__(self):
        super().__init__()
        self.image = import_files('../graphics/items', ['atkspeedboost'], size=(tile_size*2, tile_size*2))['atkspeedboost'][0]
        self.rect = self.image.get_rect(topright=(screen_width, 0))


class UltimateCharge(Item):
    def __init__(self):
        super().__init__()
        self.image = import_files('../graphics/items', ['ultimatecharge'], size=(tile_size*2, tile_size*2))['ultimatecharge'][0]
        self.rect = self.image.get_rect(topright=(screen_width, 0))


class LivePlusOne(Item):
    def __init__(self):
        super().__init__()
        self.image = import_files('../graphics/items', ['liveplus1'], size=(tile_size*2, tile_size*2))['liveplus1'][0]
        self.rect = self.image.get_rect(topright=(screen_width, 0))


item_types = [Heal, Stop, Defend, AtkBoost, AtkSpeedBoost, LivePlusOne, UltimateCharge]


def random_item():
    available_items = [i for i in item_types if not ((i == LivePlusOne and game_mode[0] in {'hard', 'easy', 'manager'}) or ((i == LivePlusOne or i == Heal) and game_mode[0] == 'crazy'))]
    return random.choice(available_items)
