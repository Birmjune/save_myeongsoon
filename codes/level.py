from tile import *
from pygame import *
from pygame.math import Vector2 as vec
from item import *
from player import Player, player_status
from enemy import *
from setup import *
from itertools import chain


wall_types = {'X': BasicWall, 'U': Up, 'D': Down, 'E': ExitPortal, 'l': ShooterLeft, 'r': ShooterRight, '<': SpikeLeft, '>': SpikeRight, '^': SpikeUp, '#': SpikeDown, 's': SummonPlace}
portalin_types = {'i': 0}
portalout_types = {'o': 0}
item_types = {'T': 0}


class Level:
    def __init__(self, level_data, surface, background):
        self.tiles = sprite.Group()
        self.player = sprite.GroupSingle()
        self.enemies = sprite.Group()
        self.boss = sprite.GroupSingle()
        self.portalins = dict()
        self.portalouts = dict()
        self.itemboxes = sprite.Group()
        self.enm_bullets = sprite.Group()
        summon_places = []

        with open(f'../maps/map{level_data}.txt') as f:
            stage_map = f.readlines()

        for row_idx, row in enumerate(stage_map):
            for col_idx, cell in enumerate(row):
                if cell == 'P':
                    player_sprite = Player(vec(col_idx*tile_size, row_idx*tile_size), status=player_status[0])
                    self.player.add(player_sprite)
                elif cell == 'R':
                    self.tiles.add(Princess(vec(col_idx*tile_size, row_idx*tile_size), tile_size))
                elif cell in enemy_dict.keys():
                    enm = enemy_dict[cell](vec(col_idx*tile_size, row_idx*tile_size))
                    self.enemies.add(enm)
                    if isinstance(enm, EnemyBoss):
                        self.boss.add(enm)
                elif cell in portalin_types:
                    self.portalins[portalin_types[cell]] = vec(col_idx*tile_size, row_idx*tile_size)
                elif cell in portalout_types:
                    self.portalouts[portalout_types[cell]] = vec(col_idx*tile_size, row_idx*tile_size)
                elif cell in item_types:
                    self.itemboxes.add(ItemBox(vec(col_idx*tile_size, row_idx*tile_size), tile_size, random_item()()))
                elif cell not in wall_types:
                    pass
                else:
                    wall = wall_types[cell]
                    wall_obj = wall(vec(col_idx * tile_size, row_idx * tile_size), tile_size)
                    if isinstance(wall_obj, Shooter):
                        self.enemies.add(wall_obj)
                    else:
                        self.tiles.add(wall_obj)
                    if cell == 's':
                        summon_places.append(vec(col_idx * tile_size, row_idx * tile_size))

        for k in self.portalins.keys():
            self.tiles.add(Portal(self.portalins[k], tile_size, self.portalouts[k], k))
            self.tiles.add(Portal(self.portalouts[k], tile_size, None, k))

        for t in self.itemboxes:
            self.tiles.add(t)

        for boss in self.boss:
            boss.summon_places = summon_places

        self.surface = surface
        self.background = background

        self.groups = [self.player, self.enemies, self.tiles]
        self.moving_groups = [self.player, self.enemies]
        self.movings = sprite.Group(*tuple(chain(group.sprites() for group in self.moving_groups)))
        self.all = sprite.Group(*tuple(chain(group.sprites() for group in self.groups)))

    # def encounter_enemy(self):
    #     player = self.player.sprite
    #     for enemy in self.enemies:
    #         if enemy.rect.colliderect(player.rect):
    #             if player.velocity.y < 0:
    #                 enemy.get_damage(player.damage)
    #             else:
    #                 player.get_damage(player.damage)
    #             enemy.knockback()
    #             player.knockback()

    def update(self):
        if self.player.sprite.effects['stopping_enemies']:
            for blt in self.enm_bullets:
                blt.kill()
        self.tiles.update(not [i for i in self.enemies.sprites() if isinstance(i, Enemy)])
        self.player.sprite.map = self.all
        self.player.update(self.enemies.sprites())
        if not self.player.sprite.effects['stopping_enemies']:
            self.enm_bullets.empty()
            for enm in self.enemies:
                if isinstance(enm, EnemyBoss):
                    self.enemies.add(enm.summoned.sprites())
                all_ = [*tuple(i for i in self.all if i is not enm)]
                enm.map = all_
                enm.update(self.player.sprites())
                self.enm_bullets.add(enm.bullets.sprites())

    def erase(self):
        # wall_tiles
        # self.tiles.draw(self.surface)

        # enemies
        for enm in self.enemies:
            enm.erase_healthbar(self.surface, self.background)
        self.enemies.clear(self.surface, self.background)

        # player
        # self.encounter_enemy()
        for player in self.player:
            player.erase_healthbar(self.surface, self.background)
            player.erase_gauge(self.surface, self.background)
            player.bullets.clear(self.surface, self.background)
            player.special_bullets.clear(self.surface, self.background)
            player.special_effect.clear(self.surface, self.background)
            player.item.clear(self.surface, self.background)
        self.player.clear(self.surface, self.background)

        self.enm_bullets.clear(self.surface, self.background)

    def draw(self):
        # wall_tiles
        self.tiles.draw(self.surface)

        # enemies
        for enm in self.enemies:
            enm.draw_healthbar(self.surface)
            try:
                enm.bullet_director.draw(self.surface)
            except AttributeError:
                pass
        self.enemies.draw(self.surface)

        # player
        # self.encounter_enemy()
        for player in self.player:
            player.draw_healthbar(self.surface)
            player.draw_gauge(self.surface)
            player.bullets.draw(self.surface)
            player.special_bullets.draw(self.surface)
            player.special_effect.draw(self.surface)
            player.item.draw(self.surface)
        self.player.draw(self.surface)

        self.enm_bullets.draw(self.surface)
