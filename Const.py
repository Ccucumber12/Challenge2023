import pygame as pg
from enum import Enum, auto, IntEnum

# model
FPS = 60 # frame per second
GAME_LENGTH = 300 * FPS

# Characters
# Player
class PLAYER_IDS(Enum):
    def __str__(self):
        return f"{self.name}"
    PLAYER0 = 0
    PLAYER1 = 1
    PLAYER2 = 2
    PLAYER3 = 3
PLAYER_INIT_POSITION = [pg.Vector2(200, 400), pg.Vector2(600, 400), pg.Vector2(200, 200), pg.Vector2(600, 200)]
PLAYER_RADIUS = 30
PLAYER_RESPAWN_TIME = 5 * FPS
PLAYER_ADD_SCORE = [2, 3, 5]
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
GHOST_INIT_SPEED = 120
GHOST_CHANTING_TIME = 2 * FPS  # chanting time before it teleport
GHOST_WANDER_TIME = 5 * FPS
GHOST_CHASE_TIME = 15 * FPS
GHOST_INIT_TP_CD = 9 * FPS
class GHOST_STATE(IntEnum):
    CHASE = 1
    WANDER = 2
    TELEPORT = 4
# patronus
PATRONUS_SPEED = PLAYER_SPEED
    
# Map
MAP_ROAD = 0
MAP_PUDDLE = 1
MAP_OBSTACLE = 2

# State machine constants
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
    PATRONUS = 3
    PETRIFICATION = 2
    SORTINGHAT = 4
class ITEM_STATUS(Enum):
    def __str__(self):
        return f"{self.name}"
    NORMAL = 0
    REVERSED = 1
    ENHANCED = 2
ITEM_GENERATE_PROBABILITY = [0, 1/4, 1/4, 1/4, 1/4] # should correspond to ITEM_SET
# The probability of golden snitch should be set to ZERO.
ITEM_STATUS_PROBABILITY = [15/15, 0/15, 0/15] # should correspond to ITEM_STATES
ITEM_DURATION = {
    ITEM_SET.GOLDEN_SNITCH: {ITEM_STATUS.NORMAL: 1},
    ITEM_SET.CLOAK: {ITEM_STATUS.NORMAL: 5*FPS, ITEM_STATUS.REVERSED: 5*FPS,ITEM_STATUS.ENHANCED: 8*FPS},
    ITEM_SET.PATRONUS: {ITEM_STATUS.NORMAL: 15*FPS, ITEM_STATUS.REVERSED: 15*FPS,ITEM_STATUS.ENHANCED: 30*FPS},
    ITEM_SET.PETRIFICATION: {ITEM_STATUS.NORMAL: 3*FPS, ITEM_STATUS.REVERSED: 3*FPS,ITEM_STATUS.ENHANCED: 6*FPS},
    ITEM_SET.SORTINGHAT: {ITEM_STATUS.NORMAL: 10*FPS, ITEM_STATUS.REVERSED: 10*FPS, ITEM_STATUS.ENHANCED: 10}
}
ITEM_GENERATE_COOLDOWN = 3*FPS
MAX_ITEM_NUMBER = 5
ITEM_WIDTH = 50
ITEM_HEIGHT = 50
ITEM_TEST_COLOR = pg.Color('violet')
SORTINGHAT_INVINCIBLE_TIME = 5*FPS
GOLDEN_SNITCH_APPEAR_TIME = 5*FPS

# view
WINDOW_CAPTION = 'Challenge 2023'
WINDOW_SIZE = (800+282, 800)
ARENA_SIZE = (800, 800)
SCORE_BOARD_SIZE = (282, 800)
TITLE_SIZE = (1168, 800)
BACKGROUND_COLOR = pg.Color('black')
PLAYER_COLOR = [pg.Color('green'), pg.Color('magenta'), pg.Color('blue'), pg.Color('gold')]
GHOST_COLOR = [pg.Color('red')]
class OBJECT_TYPE(IntEnum):
    # The number represents the order of rendering the type.
    MAP = 0
    # SCORE_BOARD = 1
    GHOST = 2
    ITEM = 3
    PLAYER = 5
class SCENE(Enum):
    TITLE = 0
    SCORE_BOARD = 1
SCOREBOARD_FONT_SIZE = 32
TIME_POSITION = [(854, 160), (912, 160), (971, 160), (1029, 160)]
SCORE_POSITION = [
    [(854, 287), (912, 287), (971, 287), (1029, 287)],
    [(854, 414), (912, 414), (971, 414), (1029, 414)],
    [(854, 540), (912, 540), (971, 540), (1029, 540)],
    [(854, 670), (912, 670), (971, 670), (1029, 670)],
]
PICTURES_PATH = {
    ITEM_SET.CLOAK: "Pictures/Items/Cloak.png",
    ITEM_SET.GOLDEN_SNITCH: "Pictures/Items/GoldenSnitch.png",
    ITEM_SET.PATRONUS: "Pictures/Items/Patronus.png",
    ITEM_SET.PETRIFICATION: "Pictures/Items/Petrification.png",
    ITEM_SET.SORTINGHAT: "Pictures/Items/SortingHat.png",
    PLAYER_IDS.PLAYER0: "Pictures/Characters/Players/Player0.png",
    PLAYER_IDS.PLAYER1: "Pictures/Characters/Players/Player1.png",
    PLAYER_IDS.PLAYER2: "Pictures/Characters/Players/Player2.png",
    PLAYER_IDS.PLAYER3: "Pictures/Characters/Players/Player3.png",
    GHOST_IDS.DEMENTOR: "Pictures/Characters/Ghosts/Dementor.png",
    SCENE.TITLE: "Pictures/Scenes/Title.png",
    SCENE.SCORE_BOARD: "Pictures/Scenes/Scoreboard.png",
}
FONT_PATH = "Fonts"

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
