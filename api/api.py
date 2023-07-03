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
    def __init__(self, _id, _position, _dead, _speed, _score, _effect):
        self.__id = _id
        self.__position = _position
        self.__dead = _dead
        self.__speed = _speed
        self.__score = _score
        self.__effect = _effect

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


class Ghost:
    def __init__(self, _id, _position, _teleport_remain, _teleport_destination):
        self.__id = _id
        self.__position = _position
        self.__teleport_remain = _teleport_remain
        self.__teleport_destination = _teleport_destination

    @property
    def id(self) -> int:
        return self.__id

    @property
    def position(self) -> Vector2:
        return self.__position

    @property
    def teleport_remain(self) -> int:
        return self.__teleport_remain

    @property
    def teleport_destination(self) -> Vector2:
        return self.__teleport_destination


class Helper:
    def get_items(self) -> list[Item]:
        pass

    def get_players(self) -> list[Player]:
        pass

    def get_ghosts(self) -> list[Ghost]:
        pass

    def get_nearest_ghost(self) -> Ghost:
        pass

    def get_nearest_item(self) -> Item:
        pass

    def get_nearest_player(self) -> Player:
        pass

    def get_farthest_ghost(self) -> Ghost:
        pass

    def get_farthest_item(self) -> Item:
        pass

    def get_farthest_player(self) -> Player:
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


def get_nearest_ghost() -> Ghost:
    return _helper.get_nearest_ghost()


def get_nearest_item() -> Item:
    return _helper.get_nearest_item()


def get_nearest_player() -> Player:
    return _helper.get_nearest_player()


def get_farthest_ghost() -> Ghost:
    return _helper.get_farthest_ghost()


def get_farthest_item() -> Item:
    return _helper.get_farthest_item()


def get_farthest_player() -> Player:
    return _helper.get_farthest_player()


def get_ground_type(position: Vector2) -> GroundType:
    return _helper.get_ground_type(position)


def get_myself() -> Player:
    return _helper.get_myself()


def distance(a: Vector2, b: Vector2) -> float:
    return _helper.distance(a, b)


def distance_to(position: Vector2) -> float:
    return _helper.distance_to(position)
