import pygame as pg
from enum import Enum, auto, IntEnum

# model
FPS = 60 # frame per second
GAME_LENGTH = 60 * FPS
PLAYER_INIT_POSITION = [pg.Vector2(200, 400), pg.Vector2(600, 400), pg.Vector2(200, 200), pg.Vector2(600, 200)]
PLAYER_RADIUS = 30
PLAYER_RESPAWN_TIME = 5 * FPS
PLAYER_ADD_SCORE = [2, 3, 5]
PLAYER_SPEED = 100
class PLAYER_IDS(Enum):
    PLAYER0 = 0
    PLAYER1 = 1
    PLAYER2 = 2
    PLAYER3 = 3
    def __str__(self):
        return f"{self.name}"
NUM_OF_PLAYERS = 4
DIRECTION_TO_VEC2 = {
    'up': pg.Vector2(0, -1),
    'left': pg.Vector2(-1, 0),
    'down': pg.Vector2(0, 1),
    'right': pg.Vector2(1, 0),
}
GHOST_INIT_POSITION = [pg.Vector2(400, 400)]
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
ITEM_DURATION = {
    "cloak": {"normal": 5*FPS, "reversed": 5*FPS,"enhanced": 8*FPS},
    "patronus": {"normal": 15*FPS, "reversed": 15*FPS,"enhanced": 30*FPS},
    "golden_stitch": {"normal": 1},
    "petrification": {"normal": 3*FPS, "reversed": 3*FPS,"enhanced": 6*FPS}
}
ITEM_GENERATE_COOLDOWN = 3*FPS
MAX_ITEM_NUMBER = 5
ITEM_WIDTH = 50
ITEM_HEIGHT = 50
ITEM_TEST_COLOR = pg.Color('violet')
SORTINGHAT_INVINCIBLE_TIME = 5*FPS
class ITEM_SET(Enum):
    GOLDEN_SNITCH = 0
    CLOAK = 1
    PETRIFICATION = 2
    PATRONUS = 3
    SORTINGHAT = 4
class ITEM_STATUS(Enum):
    NORMAL = 0
    REVERSED = 1
    ENHANCED = 2
ITEM_GENERATE_PROBABILITY = [0, 1/4, 1/4, 1/4, 1/4] # should correspond to ITEM_SET
# The probability of golden snitch should be set to ZERO.
ITEM_STATUS_PROBABILITY = [12/15, 1/15, 2/15] # should correspond to ITEM_STATES
GOLDEN_SNITCH_APPEAR_TIME = 5*FPS

# view
WINDOW_CAPTION = 'Challenge 2023'
WINDOW_SIZE = (800, 800)
ARENA_SIZE = (800, 800)
BACKGROUND_COLOR = pg.Color('black')
PLAYER_COLOR = [pg.Color('green'), pg.Color('magenta'), pg.Color('blue'), pg.Color('gold')]
GHOST_COLOR = [pg.Color('red')]
class OBJECT_TYPE(IntEnum):
    # The number represents the order of rendering the type.
    MAP = 0
    GHOST = 1
    ITEM = 2
    PLAYER = 5
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
    OBJECT_TYPE.GHOST: "Pictures/Characters/Ghosts"
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
