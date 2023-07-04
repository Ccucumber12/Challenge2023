from enum import Enum, IntEnum

import pygame as pg

# model

FPS = 60  # frame per second
GAME_LENGTH = 180 * FPS


# Characters

# Player

class PLAYER_IDS(IntEnum):
    def __str__(self):
        return f"{self.name}"
    
    PLAYER0 = 0
    PLAYER1 = 1
    PLAYER2 = 2
    PLAYER3 = 3


PLAYER_RADIUS = 30
PLAYER_RESPAWN_TIME = 5 * FPS
PLAYER_ADD_SCORE = [2, 3, 5, 5]
PLAYER_SPEED = 100
NUM_OF_PLAYERS = 4

# Ghost

class GHOST_IDS(Enum):
    def __str__(self):
        return f"{self.name}"

    DEMENTOR = 0

DIRECTION_TO_VEC2 = {
    'up': pg.Vector2(0, -1),
    'left': pg.Vector2(-1, 0),
    'down': pg.Vector2(0, 1),
    'right': pg.Vector2(1, 0),
}
GHOST_INIT_POSITION = {
    GHOST_IDS.DEMENTOR: pg.Vector2(400, 400)
}
GHOST_RADIUS = 30
GHOST_INIT_SPEED = 100
GHOST_MAX_SPEED = 180
GHOST_CHANTING_TIME = 2 * FPS  # chanting time before it teleport
GHOST_CHANTING_COLOR = pg.Color(79, 48, 114)
GHOST_WANDER_TIME = 5 * FPS
GHOST_CHASE_TIME = 15 * FPS
GHOST_INIT_TP_CD = 30 * FPS

class GHOST_STATE(IntEnum):
    CHASE = 1
    WANDER = 2
    TELEPORT = 4

CACHE_CELLS = 3

# patronus
PATRONUS_SPEED = PLAYER_SPEED
PATRONUS_RADIUS = PLAYER_RADIUS


# map
MAP_ROAD = 0
MAP_PUDDLE = 1
MAP_OBSTACLE = 2

# state machine constants

STATE_POP = 0  # for convenience, not really a state which we can be in
STATE_MENU = 1
STATE_PLAY = 2
STATE_STOP = 3  # not implemented yet
STATE_ENDGAME = 4

# item

class ITEM_SET(Enum):
    def __str__(self):
        return f"{self.name}"
    GOLDEN_SNITCH = 0
    CLOAK = 1
    PATRONUS = 2
    PETRIFICATION = 3
    SORTINGHAT = 4

ITEM_GENERATE_PROBABILITY = [0, 1 / 4, 1 / 4, 1 / 4, 1 / 4]  # should correspond to ITEM_SET
# The probability of golden snitch should be set to ZERO.
ITEM_DURATION = {
    ITEM_SET.GOLDEN_SNITCH: 1,
    ITEM_SET.CLOAK: 5 * FPS,
    ITEM_SET.PATRONUS: 15 * FPS,
    ITEM_SET.PETRIFICATION: 3 * FPS,
    ITEM_SET.SORTINGHAT: 10 * FPS
}
ITEM_LIFETIME = {
    ITEM_SET.GOLDEN_SNITCH: 3000 * FPS,
    ITEM_SET.CLOAK: 60 * FPS,
    ITEM_SET.PATRONUS: 60 * FPS,
    ITEM_SET.PETRIFICATION: 60 * FPS,
    ITEM_SET.SORTINGHAT: 60 * FPS
}
ITEM_GENERATE_COOLDOWN = 3 * FPS
MAX_ITEM_NUMBER = 10
ITEM_WIDTH = 50
ITEM_HEIGHT = 50
SORTINGHAT_INVINCIBLE_TIME = 5 * FPS
GOLDEN_SNITCH_APPEAR_TIME = 30 * FPS
GOLDEN_SNITCH_SPEED = 250

PETRIFICATION_ANIMATION_SPEED = 10
PETRIFICATION_ANIMATION_COLOR = pg.Color(169, 169, 169)
PETRIFICATION_ANIMATION_THICKNESS = 10
PETRIFICATION_ANIMATION_PARTICLE_RADIUS = 3

# viewF
WINDOW_CAPTION = 'Challenge 2023'
ARENA_SIZE = (1200, 800)
SCORE_BOARD_SIZE = (282, 800)
WINDOW_SIZE = (ARENA_SIZE[0]+SCORE_BOARD_SIZE[0], ARENA_SIZE[1])
TITLE_SIZE = (1168, 800)
FOG_SIZE = (1878, 800)
FOG_TRANSPARENCY = 150
FOG_SPEED = 150
BACKGROUND_COLOR = pg.Color('black')
CLOAK_TRANSPARENCY = 128 # Adjust the value between 0 (fully transparent) and 255 (fully opaque)
NEAR_VANISH_TRANSPARENCY = 64
SORTINGHAT_ANIMATION_SPEED = 500
SORTINGHAT_ANIMATION_ROTATE_SPEED = 60
MAGIC_CIRCLE_RADIUS = GHOST_RADIUS

class OBJECT_TYPE(IntEnum):
    # The number represents the order of rendering the type.
    MAP = 0
    # SCORE_BOARD = 1
    GHOST = 2
    ITEM = 3
    PATRONUS = 4
    PLAYER = 5

class SCENE(Enum):
    TITLE = 0
    SCORE_BOARD = 1
    FOG = 2
    ENDGAME = 3

class OTEHR_PICTURES(Enum):
    PATRONUS = 0
    MAGIC_CIRCLE = 1

SCOREBOARD_FONT_SIZE = 32
SCOREBOARD_COL = [54, 112, 171, 229]
TIME_POSITION = [(x + ARENA_SIZE[0], 160) for x in SCOREBOARD_COL]
PLAYER_NAME = ["Hermione Yellow", "Hermione Pink", "Hermione Gray", "Hermione Blue"]
NAME_ROW = [238, 365, 490, 620]
NAME_POSITION = [(140 + ARENA_SIZE[0], y) for y in NAME_ROW]
SCORE_ROW = [287, 414, 540, 670]
SCORE_POSITION = [[(x + ARENA_SIZE[0], y) for x in SCOREBOARD_COL] for y in SCORE_ROW]
class PLAYER_SKINS(Enum):
    NORMAL = 0
    SORTINGHAT = 1
PICTURES_PATH = {
    ITEM_SET.CLOAK: "pictures/items/Cloak.png",
    ITEM_SET.GOLDEN_SNITCH: "pictures/items/GoldenSnitch.png",
    ITEM_SET.PATRONUS: "pictures/items/Patronus.png",
    ITEM_SET.PETRIFICATION: "pictures/items/Petrification.png",
    ITEM_SET.SORTINGHAT: "pictures/items/SortingHat.png",
    PLAYER_IDS.PLAYER0: ["pictures/characters/players", "Player0.png"],
    PLAYER_IDS.PLAYER1: ["pictures/characters/players", "Player1.png"],
    PLAYER_IDS.PLAYER2: ["pictures/characters/players", "Player2.png"],
    PLAYER_IDS.PLAYER3: ["pictures/characters/players", "Player3.png"],
    PLAYER_SKINS.NORMAL: "normal",
    PLAYER_SKINS.SORTINGHAT: "sortinghat",
    GHOST_IDS.DEMENTOR: "pictures/characters/ghosts/Dementor.png",
    SCENE.TITLE: "pictures/scenes/Title.png",
    SCENE.SCORE_BOARD: "pictures/scenes/Scoreboard.png",
    SCENE.FOG: "pictures/scenes/Fog.png",
    SCENE.ENDGAME: "pictures/scenes/Ending.png",
    OTEHR_PICTURES.PATRONUS: "pictures/characters/shining_patronus.png",
    OTEHR_PICTURES.MAGIC_CIRCLE: "pictures/characters/ghosts/MagicCircle.png",
}
FONT_PATH = "fonts"

# sound
MUSIC_PATH = {
    STATE_MENU: "music/title_music_v3.wav",
    STATE_PLAY: "music/ingame_music_all.wav"
}

# controller
PLAYER_KEYS = {
    pg.K_UP: (3, 'up'),
    pg.K_LEFT: (3, 'left'),
    pg.K_DOWN: (3, 'down'),
    pg.K_RIGHT: (3, 'right'),
    pg.K_i: (2, 'up'),
    pg.K_j: (2, 'left'),
    pg.K_k: (2, 'down'),
    pg.K_l: (2, 'right'),
    pg.K_t: (1, 'up'),
    pg.K_f: (1, 'left'),
    pg.K_g: (1, 'down'),
    pg.K_h: (1, 'right'),
    pg.K_w: (0, 'up'),
    pg.K_a: (0, 'left'),
    pg.K_s: (0, 'down'),
    pg.K_d: (0, 'right'),
}
MUTE_KEY = pg.K_F1

# Utils

FLUCTUATION_RATIO = 0.3
