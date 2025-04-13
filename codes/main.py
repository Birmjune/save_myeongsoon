from tile import Tile
from setup import *
from support import *
# from audios import *
from end_check import *
from pygame import *
from pygame.math import Vector2 as vec
import sys
from level import Level
from player import player_status
import time as t
from sounds import bgm1, bgm2


def save(mode, level_num, time_passed, lives_left):
    with open(f'../data/save_data_{mode}.txt', 'w') as f:
        f.write(f'{level_num}\n{time_passed}\n{lives_left}')


def load(mode):
    if mode is None:
        raise FileNotFoundError
    with open(f'../data/save_data_{mode}.txt', 'r') as f:
        return tuple(i.strip() for i in f.readlines())


# General setup
init()
clock = time.Clock()
fnt = font.SysFont('segoeuisymbol', 26)
fnt_time = font.SysFont('Consolas', 26)
key.set_repeat()

# Game Screen
screen = display.set_mode((screen_width, screen_height))
display.set_caption("명순공주")

# 시작 대기 화면
black = (0,0,0)
white = (255,255,255)
fnt1 = font.SysFont('segoeuisymbol', 50)
fnt2 = font.SysFont('segoeuisymbol', 25)
fnt3 = font.SysFont('segoeuisymbol', 70)
fnt4 = font.SysFont('Consolas', 50)
# background1 = image.load("../graphics/background/night.png")
background1 = image.load("../graphics/background/evening.jpg")
background2 = image.load("../graphics/background/evening.jpg")
background3 = image.load("../graphics/background/explain.png")

# die_sound = mixer.Sound("../sounds/die_sound.ogg")

# mixer.music.load("../sounds/bgm1.wav")
# mixer.music.set_volume(0.3)
# mixer.music.play(-1)

while True:
    start = False
    msg_idx = 0
    init_msg_keys = ['load', 'game modes', 'quit']
    init_msg = {'game modes': ['easy', 'normal', 'hard', 'crazy'], 'load': ['new game', 'load'], 'quit': ['quit']}
    max_length_msg = max(max(len(j) for j in i) for i in init_msg.values())
    idx_keys = ['load_idx', 'mode_idx', 'quit']
    idxs = {'mode_idx': 0, 'load_idx': 0, 'quit': 0}


    while not start:
        clock.tick(60)
        for evt in event.get():
            if evt.type == KEYDOWN:
                if evt.key in {K_SPACE, K_RETURN}:
                    start = True
                elif evt.key in {K_LEFT}:
                    if init_msg_keys[msg_idx] == 'game modes':
                        idxs['mode_idx'] = (idxs['mode_idx']-1) % len(init_msg['game modes'])
                    elif init_msg_keys[msg_idx] == 'load':
                        idxs['load_idx'] = (idxs['load_idx']-1) % len(init_msg['load'])
                elif evt.key in {K_RIGHT}:
                    if init_msg_keys[msg_idx] == 'game modes':
                        idxs['mode_idx'] = (idxs['mode_idx'] + 1) % len(init_msg['game modes'])
                    elif init_msg_keys[msg_idx] == 'load':
                        idxs['load_idx'] = (idxs['load_idx'] + 1) % len(init_msg['load'])
                elif evt.key in {K_UP}:
                    msg_idx = (msg_idx - 1) % len(init_msg_keys)
                elif evt.key in {K_DOWN}:
                    msg_idx = (msg_idx + 1) % len(init_msg_keys)
                elif evt.key == K_m and init_msg_keys[msg_idx] == 'game modes':
                    game_mode[0] = 'manager'
            if evt.type == QUIT:
                SB = 1
                quit()
                sys.exit()

        screen.blit(background2, (0, 0))
        write(screen, 'Save MyeongSoon!', (screen_width // 2, 10), fnt1, None, black)
        write(screen, '<Keys>\n\nMove and Jump: WASD or arrows\n\nAttack: F\n\nUse Item: Space\n\n Use Ultimate: S\n\nSave: 0', (screen_width // 4, 100), fnt2, None, black)
        write(screen, '<Extra>\n\nTime limit: ' + str(int(max_time)) + 's', (screen_width * 3 // 4, 100), fnt2, None, black)
        write(screen, '\n\n\n\n\n<Game modes>\n\nEasy: Infinite hearts\n\nNormal: 20 hearts\n\nHard: 1 heart\n\nCrazy: 1 hp (1 hit then die)', (screen_width * 3 // 4, 100), fnt2, None, black)
        write(screen, '(Change mode with ←,→)', (screen_width // 4 + 10, 535), fnt2, None, black)
        for msg_num, msg in enumerate(init_msg_keys):
            write(screen, '{0:^{1}}'.format(init_msg[msg][idxs[idx_keys[msg_num]]], max_length_msg + 2), (screen_width // 2, screen_height * 3 // 5 + 60 * msg_num), fnt4, None, black, outline_color=((0, 255, 255) if msg_num == msg_idx else None))
        display.flip()

    if init_msg_keys[msg_idx] == 'quit':
        sys.exit()
    if not game_mode[0]:
        game_mode[0] = init_msg['game modes'][idxs['mode_idx']]
    timeover = False

    if init_msg['load'][idxs['load_idx']] == 'load':
        try:
            data = load(game_mode[0])
            loaded = True
            break
        except FileNotFoundError:
            loaded = False
            screen.blit(background2, (0, 0))
            write(screen, 'There is no data to load\n', (screen_width // 2, screen_height // 2), fnt3, message_color=(255, 0, 0))
            display.flip()
            t.sleep(1)
    else:
        loaded = False
        break

bgs = [background1, background1, background1, background1, background1, background1, background1, background1, background1]
bgms = [bgm1, bgm1, bgm1, bgm1, bgm1, bgm2, bgm1, bgm1, bgm2]
start_ = False
blink = 0
while not start_:
    clock.tick(60)
    for evt in event.get():
        if evt.type == KEYDOWN:
            if evt.key in {K_SPACE, K_RETURN}:
                start_ = True
        if evt.type == QUIT:
            SB = 1
            quit()
            sys.exit()
    blink += 1/60
    screen.blit(background3, (0, 0))
    if int(blink)%2:
        write(screen, 'Press Space To Start\n', (screen_width // 2, screen_height // 2), fnt3, message_color=(255, 0, 0), bg_color=None, outline_color=(255, 255, 0, 255))
    display.flip()

key.set_repeat(1, 1)

if loaded:
    lives = eval(data[2])
elif game_mode[0] in {'normal'}:
    lives = max_lives
elif game_mode[0] in {'hard', 'crazy'}:
    lives = 1
elif game_mode[0] in {'easy', 'manager'}:
    lives = None
else:
    lives = None

start_time = t.perf_counter() - (0 if not loaded else float(data[1]))

save_cooltime = int(0.5*fps)
i = 1 if not loaded else int(data[0])
while i < max_level:
    # level
    level = Level(i, screen, bgs[i])
    screen.blit(bgs[i], (0, 0))
    level.tiles.draw(level.surface)
    sound = bgms[i]
    sound.play(-1)
    while True:
        score = t.perf_counter() - start_time
        if game_end[0]:
            sound.stop()
            break
        if level_end[0]:
            sound.stop()
            start_level()
            if i != max_level-1:
                screen.blit(background2, (0, 0))
                write(screen, f'Level {i} -> {i+1}\n', (screen_width // 2, screen_height // 2), fnt3, bg_color=None, message_color=(255, 0, 0))
                display.flip()
            t.sleep(0.5)
            break
        if live_plus_1[0]:
            lives += 1
            live_plus_1[0] = False
        for evt in event.get():
            if evt.type == QUIT:
                quit()
                sys.exit()
            if evt.type == KEYDOWN:
                if evt.key == K_0 and save_cooltime == 0:
                    save(game_mode[0], i, score, lives)
                    screen.blit(background2, (0, 0))
                    write(screen, 'SAVED\n', (screen_width // 2, screen_height // 2), fnt3, bg_color=None, message_color=(255, 0, 0))
                    display.flip()
                    t.sleep(0.5)
                    print(t.time())
                    save_cooltime = int(0.5*fps)
                if game_mode[0] == 'manager':
                    level_dict = {K_1: 1, K_2: 2, K_3: 3, K_4: 4, K_5: 5, K_6: 6, K_7: 7, K_8: 8}
                    if evt.key in level_dict.keys():
                        i = level_dict[evt.key]
                        break
                    if evt.key == K_9:
                        for enm in level.enemies.sprites():
                            enm.kill()
                # elif evt.key == K_2:
                #     level.player.sprite.rect.x = level.enemies.sprites()[0].rect.x
                # elif evt.key == K_3:
                #     level.enemies.sprites()[0].rect.x = level.player.sprite.rect.x

        save_cooltime -= 1 if save_cooltime else 0

        # Drawing
        screen.blit(bgs[i], (0, 0))
        # screen.fill((255, 255, 255))
        level.update()
        level.erase()
        level.draw()
        write(screen, '{0:0>{1}.3f}'.format(score, len(str(int(max_time)))+4), (0, 0), fnt_time, bg_color=None, pos='topleft', outline_color=(255, 255, 0))
        if lives is not None:
            write(screen, chr(10084)+chr(10006)+'{}'.format(lives), (screen_width//2-5, 0), fnt, bg_color=None, pos='topleft', outline_color=(255, 255, 0))

        display.flip()

        clock.tick(fps)

        if score >= max_time:
            timeover = True
            break

    if game_end[0]:
        if game_mode[0] in {'hard', 'crazy'} or lives == 1:
            # screen.fill((255, 255, 255))
            screen.blit(background2, (0, 0))
            write(screen, 'Game Over\n', (screen_width//2, screen_height//2), fnt3, bg_color=None, message_color=(255, 0, 0))
            display.flip()
            t.sleep(3)
            break
        elif game_mode[0] in {'normal'}:
            lives -= 1
            game_end[0] = False
            # screen.fill((255, 255, 255))
            screen.blit(background2, (0, 0))
            write(screen, 'You Died', (screen_width//2, screen_height//2), fnt3, bg_color=None, message_color=(255, 0, 0))
            display.flip()
            t.sleep(0.5)
            player_status[0] = None
            continue
        elif game_mode[0] in {'easy', 'manager'}:
            game_end[0] = False
            # screen.fill((255, 255, 255))
            screen.blit(background2, (0, 0))
            write(screen, 'You Died', (screen_width//2, screen_height//2), fnt3, bg_color=None, message_color=(255, 0, 0))
            display.flip()
            t.sleep(0.5)
            player_status[0] = None
            continue
    if timeover:
        # screen.fill((255, 255, 255))
        screen.blit(background2, (0, 0))
        write(screen, 'Time Over\n', (screen_width//2, screen_height//2), fnt3, message_color=(255, 0, 0))
        display.flip()
        t.sleep(3)
        break
    i += 1
else:
    if game_mode[0] == 'manager':
        screen.blit(background2, (0, 0))
        write(screen, 'End of Game\n', (screen_width//2, screen_height//2), fnt3, message_color=(255, 0, 0))
        display.flip()
        t.sleep(3)
    else:
        end_time = t.perf_counter()

        key.set_repeat()

        screen = display.set_mode((screen_width, screen_height))
        screen.fill((255, 255, 255))

        try:
            with open(f'../rankers/rankers_{game_mode[0]}.txt') as ranks:
                rankers = [[j.strip() for j in i.split('\t')] for i in ranks]
        except FileNotFoundError:
            rankers = []

        score = end_time - start_time

        if not rankers:
            user_name = get_input(screen, 'your name', fnt)
            rankers.append([user_name, '{0:.3f}'.format(score)])
            with open(f'../rankers/rankers_{game_mode[0]}.txt', 'w') as ranks:
                ranks.write('\n'.join(['\t'.join(i) for i in rankers]))
        elif score < float(rankers[-1][1]) or len(rankers) < 10:
            user_name = get_input(screen, 'your name', fnt)
            rankers.append([user_name, '{0:.3f}'.format(score)])
            rankers.sort(key=lambda x: float(x[1]))
            rankers = rankers[:10]
            with open(f'../rankers/rankers_{game_mode[0]}.txt', 'w') as ranks:
                ranks.write('\n'.join(['\t'.join(i) for i in rankers]))
        msg = 'Rankers\n\n' + '\n'.join('{0:0>2} {1:^{2}} {3:0>{4}}'.format(i+1, ranker[0], max(len(i[0]) for i in rankers), ranker[1], max(len(i[1]) for i in rankers)) for i, ranker in enumerate(rankers)) + '\n\nPress r to reset'
        write(screen, msg, (screen_width//2, screen_height//4), fnt)

        display.update()
        # key.set_repeat(1, 1)
        asking = False
        while True:
            for evt in event.get():
                if evt.type == QUIT:
                    sys.exit()
                elif evt.type == KEYDOWN:
                    if evt.key == K_r:
                        asking = True
                    elif evt.key == K_y:
                        if asking:
                            rankers.clear()
                            asking = False
                            with open(f'../rankers/rankers_{game_mode[0]}.txt', 'w') as ranks:
                                ranks.write('')
                    elif evt.key == K_n:
                        asking = False
            if asking:
                write(screen, 'Really clear the ranking?\n\n[y/n]', (screen_width // 2, screen_height // 4), fnt)
            else:
                msg = 'Rankers\n\n' + '\n'.join('{0:0>2} {1:^{2}} {3:0>{4}}'.format(i + 1, ranker[0], max(len(i[0]) for i in rankers), ranker[1], max(len(i[1]) for i in rankers)) for i, ranker in enumerate(rankers)) + '\n'*(10-len(rankers)) + '\n\nPress r to reset'
                write(screen, msg, (screen_width // 2, screen_height // 4), fnt)
            display.flip()
