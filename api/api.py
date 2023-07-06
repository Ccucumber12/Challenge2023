from enum import Enum, auto

from pygame import Vector2


class AI:
    def player_tick(self) -> Vector2:
        pass


class GroundType(Enum):

    @staticmethod
    def get_by_num(num):
        if num == 0:
            return GroundType.ROAD
        elif num == 1:
            return GroundType.PUDDLE
        elif num == 2:
            return GroundType.OBSTACLE
        else:
            return None

    ROAD = auto()
    PUDDLE = auto()
    OBSTACLE = auto()


class ItemType(Enum):
    @staticmethod
    def get_by_name(s):
        for i in ItemType:
            if i.name == s:
                return i
        return None

    GOLDEN_SNITCH = auto()
    CLOAK = auto()
    PATRONUS = auto()
    PETRIFICATION = auto()
    SORTINGHAT = auto()
    REMOVED_SORTINGHAT = auto()


class Item:
    def __init__(self, _id, _type, _position):
        self.__id = _id
        self.__type = _type
        self.__position = _position

    @property
    def id(self) -> int:
        return self.__id

    @property
    def type(self) -> ItemType:
        return self.__type

    @property
    def position(self) -> Vector2:
        return self.__position


class Player:
    def __init__(self, _id, _position, _dead, _speed, _score, _effect, _effect_remain):
        self.__id = _id
        self.__position = _position
        self.__dead = _dead
        self.__speed = _speed
        self.__score = _score
        self.__effect = _effect
        self.__effect_remain = _effect_remain

    @property
    def id(self) -> int:
        return self.__id

    @property
    def position(self) -> Vector2:
        return self.__position

    @property
    def dead(self) -> bool:
        return self.__dead

    @property
    def speed(self) -> float:
        return self.__speed

    @property
    def score(self) -> int:
        return self.__score

    @property
    def effect(self) -> ItemType:
        return self.__effect

    @property
    def effect_remain(self) -> int:
        return self.__effect_remain


class Ghost:
    def __init__(self, _id, _position, _speed, _teleport_destination, _teleport_after, _teleport_cooldown_remain):
        self.__id = _id
        self.__position = _position
        self.__speed = _speed
        self.__teleport_destination = _teleport_destination
        self.__teleport_after = _teleport_after
        self.__teleport_cooldown_remain = _teleport_cooldown_remain

    @property
    def id(self) -> int:
        return self.__id

    @property
    def position(self) -> Vector2:
        return self.__position

    @property
    def speed(self) -> float:
        return self.__speed

    @property
    def teleport_destination(self) -> Vector2:
        return self.__teleport_destination

    @property
    def teleport_after(self) -> int:
        return self.__teleport_after

    @property
    def teleport_cooldown_remain(self) -> int:
        return self.__teleport_cooldown_remain


class Patronus:
    def __init__(self, _id, _position, _owner):
        self.__id = _id
        self.__position = _position
        self.__owner = _owner

    @property
    def id(self) -> int:
        return self.__id

    @property
    def position(self) -> int:
        return self.__position

    @property
    def owner(self) -> int:
        return self.__owner


class Portkey:
    def __init__(self, _position, _to):
        self.__position = _position
        self.__to = _to

    @property
    def position(self):
        return self.__position

    @property
    def to(self):
        return self.__to


class Helper:
    def get_items(self) -> list[Item]:
        pass

    def get_players(self) -> list[Player]:
        pass

    def get_ghosts(self) -> list[Ghost]:
        pass

    def get_patronuses(self) -> list[Patronus]:
        pass

    def get_portkeys(self) -> list[Portkey]:
        pass

    def get_nearest_ghost(self) -> Ghost:
        pass

    def get_nearest_item(self) -> Item:
        pass

    def get_nearest_player(self) -> Player:
        pass

    def get_ground_type(self, position: Vector2) -> GroundType:
        pass

    def get_myself(self) -> Player:
        pass

    def distance(self, a: Vector2, b: Vector2) -> float:
        pass

    def distance_to(self, position: Vector2) -> float:
        pass


_helper: Helper = None


def _set_helper(helper):
    global _helper
    _helper = helper


def get_items() -> list[Item]:
    return _helper.get_items()


def get_players() -> list[Player]:
    return _helper.get_players()


def get_ghosts() -> list[Ghost]:
    return _helper.get_ghosts()


def get_patronuses() -> list[Patronus]:
    return _helper.get_patronuses()


def get_portkeys() -> list[Portkey]:
    return _helper.get_portkeys()


def get_nearest_ghost() -> Ghost:
    return _helper.get_nearest_ghost()


def get_nearest_item() -> Item:
    return _helper.get_nearest_item()


def get_nearest_player() -> Player:
    return _helper.get_nearest_player()


def get_ground_type(position: Vector2) -> GroundType:
    return _helper.get_ground_type(position)


def get_myself() -> Player:
    return _helper.get_myself()


def distance(a: Vector2, b: Vector2) -> float:
    return _helper.distance(a, b)


def distance_to(position: Vector2) -> float:
    return _helper.distance_to(position)
