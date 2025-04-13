import os
import sys
from pygame import *
from pygame.math import Vector2 as vec
from setup import *


def import_files(path, dirs, size=(tile_size, tile_size)):
    result_dict = dict(zip(dirs, [[] for i in dirs]))
    for directory in dirs:
        for _, __, img_files in os.walk(path+'/'+str(directory)):
            for img_file in img_files:
                result_dict[directory].append(transform.scale(image.load(path+'/'+str(directory)+'/'+img_file).convert_alpha(), size))

    return result_dict
    # return dict(zip(dirs, [[image.load(path+'/'+directory+'/'+img).convert_alpha() for img in list(os.walk(path+'/'+directory))] for directory in dirs]))


def get_input(screen, message, fnt):
    inp = ''
    end = False
    while not end:
        for evt in event.get():
            if evt.type == KEYDOWN:
                # if evt.unicode.isalpha():
                #     inp += evt.unicode
                # elif evt.key == K_BACKSPACE:
                #     inp = inp[:-1]
                # elif evt.key == K_RETURN:
                #     end = True
                if evt.key == K_BACKSPACE:
                    inp = inp[:-1]
                elif evt.key in [K_DELETE]:
                    inp = ''
                elif evt.key in [K_RETURN, K_KP_ENTER]:
                    end = True
                elif evt.key == K_TAB:
                    pass
                elif len(inp) < 20:
                    inp += evt.unicode
            elif evt.type == QUIT:
                sys.exit()
        write(screen, message + '\n' + inp, (screen_width//2, screen_height//3), fnt)
        display.flip()

    return inp


def write(screen, message, position, fnt, bg_color=(255, 255, 255), message_color=(0, 0, 0), outline_color=None, pos='center'):
    if bg_color is not None:
        screen.fill(bg_color)
    for i, line in enumerate(message.split('\n')):
        txt = fnt.render(line, True, message_color)
        if pos == 'center':
            p = vec(*position) + vec(-txt.get_width() // 2, i * txt.get_height())
        elif pos == 'topleft':
            p = vec(*position) + vec(0, i * txt.get_height())
        else:
            raise NotImplementedError
        if outline_color is not None:
            draw.rect(screen, outline_color, [*tuple(p), txt.get_width(), txt.get_height()])
        screen.blit(txt, tuple(p))
