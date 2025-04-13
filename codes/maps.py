from PIL import Image
from setup import *
from colors import *


def mapconvert(Path, map_num):
    img = Image.open(Path)
    img = img.convert('RGB')
    pixelsize = img.size[0]//(screen_width//tile_size)
    map_str = ''
    for i in range(screen_height//tile_size):
        s = ''
        for j in range(screen_width//tile_size):
            xcoor = j*pixelsize+1
            ycoor = i*pixelsize+1
            colors = img.getpixel((xcoor, ycoor))
            if colors == player:
                s += 'P'
            elif colors == spikeup:
                s += '^'
            elif colors == spikeright:
                s += '>'
            elif colors == spikeleft:
                s += '<'
            elif colors == spikedown:
                s += '#'
            elif colors == basicwall:
                s += 'X'
            elif colors == exit_portal:
                s += 'E'
            elif colors == itembox:
                s += 'T'
            elif colors == enemy1:
                s += '1'
            elif colors == enemy2:
                s += '2'
            elif colors == portal_in:
                s += 'i'
            elif colors == portal_out:
                s += 'o'
            elif colors == up:
                s += 'U'
            elif colors == down:
                s += 'D'
            elif colors == shooter_left:
                s += 'l'
            elif colors == shooter_right:
                s += 'r'
            elif colors == summon_place:
                s += 's'
            else:
                s += '.'
        map_str += s + '\n'
    with open(f'../maps/map{map_num}.txt', 'w') as m:
        m.write(map_str)


if __name__ == '__main__':
    mapconvert(r'C:\Users\jwc30\Documents\카카오톡 받은 파일\1.png', 5)
