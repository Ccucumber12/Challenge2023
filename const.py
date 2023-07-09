from enum import Enum, IntEnum, auto

import pygame as pg

# model

FPS = 30  # frame per second
GAME_LENGTH = 180 * FPS


# Characters

# Player

class PlayerIds(IntEnum):
    def __str__(self):
        return f"{self.name}"

    PLAYER0 = 0
    PLAYER1 = 1
    PLAYER2 = 2
    PLAYER3 = 3


PLAYER_RADIUS = 30
PLAYER_RESPAWN_TIME = 5 * FPS
PLAYER_ADD_SCORE = [2, 3, 5, 5]
PLAYER_SPEED = 100 / FPS
NUM_OF_PLAYERS = 4

# Ghost

class GhostIds(Enum):
    def __str__(self):
        return f"{self.name}"

    DEMENTOR = 0

DIRECTION_TO_VEC2 = {
    'up': pg.Vector2(0, -1),
    'left': pg.Vector2(-1, 0),
    'down': pg.Vector2(0, 1),
    'right': pg.Vector2(1, 0),
}
GHOST_RADIUS = 30
GHOST_INIT_SPEED = 100 / FPS
GHOST_MAX_SPEED = 180 / FPS
GHOST_CHANTING_TIME = 2 * FPS  # chanting time before it teleport
GHOST_CHANTING_COLOR = pg.Color(79, 48, 114)
GHOST_WANDER_TIME = 3 * FPS
GHOST_CHASE_TIME = 10 * FPS
GHOST_INIT_TP_CD = 25 * FPS

class GhostState(IntEnum):
    CHASE = 1
    WANDER = 2
    TELEPORT = 4

CACHE_CELLS = 3

class GhostSkins(Enum):
    NORMAL = 0
    KILLING = 1

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

class ItemType(Enum):
    def __str__(self):
        return f"{self.name}"
    
    GOLDEN_SNITCH = auto()
    CLOAK = auto()
    PATRONUS = auto()
    PETRIFICATION = auto()
    SORTINGHAT = auto()

class EffectType(Enum):
    CLOAK = auto()
    PATRONUS = auto()
    PETRIFICATION = auto()
    SORTINGHAT = auto()
    REMOVED_SORTINGHAT = auto()

ITEM_GENERATE_PROBABILITY = [0, 1 / 4, 1 / 4, 1 / 4, 1 / 4]  # should correspond to ITEM_SET
# The probability of golden snitch should be set to ZERO.
ITEM_DURATION = {
    EffectType.PATRONUS: 15 * FPS,
    EffectType.CLOAK: 5 * FPS,
    EffectType.PETRIFICATION: 3 * FPS,
    EffectType.SORTINGHAT: 10 * FPS,
    EffectType.REMOVED_SORTINGHAT: 5 * FPS
}
ITEM_LOSE_EFFECT_HINT_TIME = 2*FPS
ITEM_LIFETIME = {
    ItemType.GOLDEN_SNITCH: 3000 * FPS,
    ItemType.CLOAK: 60 * FPS,
    ItemType.PATRONUS: 60 * FPS,
    ItemType.PETRIFICATION: 60 * FPS,
    ItemType.SORTINGHAT: 60 * FPS
}
ITEM_GENERATE_COOLDOWN = 3 * FPS
MAX_ITEM_NUMBER = 10
ITEM_RADIUS = 25
SORTINGHAT_INVINCIBLE_TIME = 5 * FPS
GOLDEN_SNITCH_APPEAR_TIME = 120 * FPS
GOLDEN_SNITCH_SPEED = 200 / FPS

PETRIFICATION_ANIMATION_SPEED = 1000 / FPS
PETRIFICATION_ANIMATION_COLOR = pg.Color(169, 169, 169)
PETRIFICATION_ANIMATION_THICKNESS = 10
PETRIFICATION_ANIMATION_PARTICLE_RADIUS = 3

# view
WINDOW_CAPTION = 'Challenge 2023'
ARENA_SIZE = (1200, 800)
SCORE_BOARD_SIZE = (282, 800)
WINDOW_SIZE = (ARENA_SIZE[0] + SCORE_BOARD_SIZE[0], ARENA_SIZE[1])
TITLE_SIZE = (1168, 800)
ENDGAME_SIZE = (1572, 800)
FOG_SIZE = (1878, 800)
FOG_TRANSPARENCY = 150
FOG_SPEED = 150 / FPS
HELPER_SIZE = (WINDOW_SIZE[0] - 100, WINDOW_SIZE[1] - 100)

BACKGROUND_COLOR = pg.Color('black')
CLOAK_TRANSPARENCY = 128  # Adjust the value between 0 (fully transparent) and 255 (fully opaque)
NEAR_VANISH_TRANSPARENCY = 64
SORTINGHAT_ANIMATION_SPEED = 500
SORTINGHAT_ANIMATION_ROTATE_SPEED = 60
MAGIC_CIRCLE_RADIUS = GHOST_RADIUS
GHOST_KILL_ANIMATION_TIME = FPS // 3
ANIMATION_PICTURE_LENGTH = FPS // 3
DEMENTOR_PICTURE_NUMBER = 3

class ObjectType(IntEnum):
    # The number represents the order of rendering the type.
    MAP = 0
    ITEM = 3
    PATRONUS = 4
    PLAYER = 5
    GHOST = 6

class Scene(Enum):
    TITLE = 0
    SCORE_BOARD = 1
    FOG = 2
    ENDGAME = 3

class OtherPictures(Enum):
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

class PlayerSkins(Enum):
    NORMAL = 0
    SORTINGHAT = 1
    SHINING = 2
    DEAD = 3

class CharacterDirection(Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

SHINING_PLAYER_SIZE = {
    CharacterDirection.UP: (78, 78),
    CharacterDirection.LEFT: (64, 64),
    CharacterDirection.DOWN: (73, 73),
    CharacterDirection.RIGHT: (64, 64),
}

DEAD_PLAYER_SIZE = {
    CharacterDirection.UP: (64, 64),
    CharacterDirection.LEFT: (60, 60),
    CharacterDirection.DOWN: (66, 66),
    CharacterDirection.RIGHT: (60, 60),
}

PICTURES_PATH = {
    ItemType.CLOAK: "pictures/items/Cloak.png",
    ItemType.GOLDEN_SNITCH: "pictures/items/GoldenSnitch.png",
    ItemType.PATRONUS: "pictures/items/Patronus.png",
    ItemType.PETRIFICATION: "pictures/items/Petrification.png",
    ItemType.SORTINGHAT: "pictures/items/SortingHat.png",
    PlayerIds.PLAYER0: "pictures/characters/players/player0",
    PlayerIds.PLAYER1: "pictures/characters/players/player1",
    PlayerIds.PLAYER2: "pictures/characters/players/player2",
    PlayerIds.PLAYER3: "pictures/characters/players/player3",
    PlayerSkins.NORMAL: "normal",
    PlayerSkins.SORTINGHAT: "sortinghat",
    PlayerSkins.SHINING: "shining",
    PlayerSkins.DEAD: "dead",
    CharacterDirection.UP: "rear.png",
    CharacterDirection.LEFT: "left.png",
    CharacterDirection.DOWN: "front.png",
    CharacterDirection.RIGHT: "right.png",
    GhostIds.DEMENTOR: "pictures/characters/ghosts/dementor",
    GhostSkins.KILLING: "pictures/characters/ghosts/dementor/killing",
    Scene.TITLE: "pictures/scenes/Title.png",
    Scene.SCORE_BOARD: "pictures/scenes/Scoreboard.png",
    Scene.FOG: "pictures/scenes/Fog.png",
    Scene.ENDGAME: "pictures/scenes/Ending.png",
    OtherPictures.PATRONUS: "pictures/characters/shining_patronus.png",
    OtherPictures.MAGIC_CIRCLE: "pictures/characters/ghosts/MagicCircle.png",
}
FONT_PATH = "fonts"

# end game
PODIUM_POSITION = [(WINDOW_SIZE[0] / 2, 330), (WINDOW_SIZE[0] / 2 - 247, 470), 
                   (WINDOW_SIZE[0] / 2 + 260, 496)]
FINAL_SCORE_POSITION = [(x, y - 2 * PLAYER_RADIUS - 30) for (x, y) in PODIUM_POSITION]

# sound
MUSIC_PATH = {
    STATE_MENU: "music/BGM/title_music_v3.wav",
    STATE_PLAY: "music/BGM/Challenge_ingame_music_ver2.wav"
}
EFFECT_SOUND_DIR = "music/effect"
EFFECT_SOUND_PATH = {
    EffectType.CLOAK: "invisible_v2.wav",
    EffectType.PATRONUS: "get_patronus_v2.wav",
    EffectType.PETRIFICATION: "stone_v2.wav",
    EffectType.REMOVED_SORTINGHAT: "sorting_hat.wav",
    GhostState.TELEPORT: "teleport_v2.wav"
}

# controller
PLAYER_KEYS = {
    PlayerIds.PLAYER0: {pg.K_w: pg.Vector2(0, -1), pg.K_s: pg.Vector2(0, 1),
                        pg.K_a: pg.Vector2(-1, 0), pg.K_d: pg.Vector2(1, 0)},
    PlayerIds.PLAYER1: {pg.K_t: pg.Vector2(0, -1), pg.K_g: pg.Vector2(0, 1),
                        pg.K_f: pg.Vector2(-1, 0), pg.K_h: pg.Vector2(1, 0)},
    PlayerIds.PLAYER2: {pg.K_i: pg.Vector2(0, -1), pg.K_k: pg.Vector2(0, 1),
                        pg.K_j: pg.Vector2(-1, 0), pg.K_l: pg.Vector2(1, 0)},
    PlayerIds.PLAYER3: {pg.K_UP: pg.Vector2(0, -1), pg.K_DOWN: pg.Vector2(0, 1),
                        pg.K_LEFT: pg.Vector2(-1, 0), pg.K_RIGHT: pg.Vector2(1, 0)}
}
MUTE_BGM_KEY = pg.K_F1
MUTE_EFFECT_SOUND_KEY = pg.K_F2

# Utils

FLUCTUATION_RATIO = 0.3

# Others
MAP_DIR = "maps"
