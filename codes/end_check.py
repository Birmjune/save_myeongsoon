level_end = [False]
game_end = [False]


def end_game():
    global game_end
    game_end[0] = True


def end_level():
    global level_end
    level_end[0] = True


def start_level():
    global level_end
    level_end[0] = False
