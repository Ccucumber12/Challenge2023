from enum import Enum, auto

from pygame import Vector2


class AI:
    def player_tick(self) -> Vector2:
        pass


class GroundType(Enum):
    """
    地面類型
    """

    @staticmethod
    def get_by_num(num):
        if num == 0:
            return GroundType.ROAD
        elif num == 1:
            return GroundType.SLOW
        elif num == 2:
            return GroundType.OBSTACLE
        else:
            return None

    ROAD = auto()
    """
    可以正常行走的道路
    """
    SLOW = auto()
    """
    緩速帶，可以行走，行走時會緩速
    """
    OBSTACLE = auto()
    """
    障礙物，不可通行
    """


class ItemType(Enum):
    """
    道具類型
    """
    @staticmethod
    def get_by_name(s):
        for i in ItemType:
            if i.name == s:
                return i
        return None

    GOLDEN_SNITCH = auto()
    """
    金探子
    """
    CLOAK = auto()
    """
    隱形斗篷
    """
    PATRONUS = auto()
    """
    護法
    """
    PETRIFICATION = auto()
    """
    石化
    """
    SORTINGHAT = auto()
    """
    分類帽
    """


class EffectType(Enum):
    """
    玩家身上生效中的道具效果類型
    """
    @staticmethod
    def get_by_name(s):
        for i in EffectType:
            if i.name == s:
                return i
        return None

    CLOAK = auto()
    """
    隱形斗篷
    """
    PATRONUS = auto()
    """
    護法
    """
    PETRIFICATION = auto()
    """
    石化
    """
    SORTINGHAT = auto()
    """
    還在頭上的分類帽
    """
    REMOVED_SORTINGHAT = auto()
    """
    分類帽消失後短暫的無敵狀態
    """
    NONE = auto()
    """
    沒有生效中的道具效果
    """


class Item:
    """
    地圖上出現的可撿的道具。
    """
    def __init__(self, _id: int, _type: ItemType, _position: Vector2):
        self.__id = _id
        self.__type = _type
        self.__position = _position.copy()

    @property
    def id(self) -> int:
        """
        道具編號，整場遊戲中出現的每一個道具都有不同編號。
        """
        return self.__id

    @property
    def type(self) -> ItemType:
        """
        道具類型。
        """
        return self.__type

    @property
    def position(self) -> Vector2:
        """
        道具位置。
        """
        return self.__position


class Player:
    """
    玩家。
    """
    def __init__(self,
                 _id: int,
                 _position: Vector2,
                 _dead: bool,
                 _respawn_after: int,
                 _speed: float,
                 _score: int,
                 _effect: EffectType,
                 _effect_remain: int,
                 _caught_golden_snitch: bool):
        self.__id = _id
        self.__position = _position.copy()
        self.__dead = _dead
        self.__respawn_after = _respawn_after
        self.__speed = _speed
        self.__score = _score
        self.__effect = _effect
        self.__effect_remain = _effect_remain
        self.__caught_golden_snitch = _caught_golden_snitch

    @property
    def id(self) -> int:
        """
        玩家編號，每一個玩家都有不同編號。
        """
        return self.__id

    @property
    def position(self) -> Vector2:
        """
        玩家位置。
        """
        return self.__position

    @property
    def dead(self) -> bool:
        """
        是否在死亡狀態。
        """
        return self.__dead

    @property
    def respawn_after(self) -> int:
        """
        多少 tick 以後復活。如果不是死亡狀態（`dead == False`）的話則是 `-1`。
        """
        return self.__respawn_after

    @property
    def speed(self) -> float:
        """
        當前移動速度，受是否抓過金探子。（`.caught_golden_snitch`）與所在位置的地面類型影響。
        """
        return self.__speed

    @property
    def score(self) -> int:
        """
        目前擁有的分數。
        """
        return self.__score

    @property
    def effect(self) -> EffectType:
        """
        身上效果的類型，沒有的話是 `EffectType.NONE`。注意金探子的效果是永久效果，不被視為是道具效果，因此要判斷是否有金探子效果請用 `.caught_golden_snitch`。
        """
        return self.__effect

    @property
    def effect_remain(self) -> int:
        """
        效果在多少 tick 以後會失效，如果身上沒有效果（`.effect == EffectType.NONE`）的話是 `0`。
        """
        return self.__effect_remain

    @property
    def caught_golden_snitch(self) -> bool:
        """
        是否抓到過金探子。
        """
        return self.__caught_golden_snitch


class Ghost:
    """
    鬼。
    """
    def __init__(self,
                 _id: int,
                 _position: Vector2,
                 _speed: float,
                 _chanting: bool,
                 _teleport_destination: Vector2,
                 _teleport_after: int,
                 _teleport_cooldown_remain: int):
        self.__id = _id
        self.__position = _position.copy()
        self.__speed = _speed
        self.__chanting = _chanting
        self.__teleport_destination = _teleport_destination.copy()
        self.__teleport_after = _teleport_after
        self.__teleport_cooldown_remain = _teleport_cooldown_remain

    @property
    def id(self) -> int:
        """
        鬼的編號，每一隻鬼都有不同編號。
        """
        return self.__id

    @property
    def position(self) -> Vector2:
        """
        鬼的位置。
        """
        return self.__position

    @property
    def speed(self) -> float:
        """
        當前移動速度，會隨時間增加且受所在位置的地面類型影響。
        """
        return self.__speed

    @property
    def chanting(self) -> bool:
        """
        是否正在傳送詠唱。
        """
        return self.__chanting

    @property
    def teleport_destination(self) -> Vector2:
        """
        目前詠唱中的傳送目標，如果沒有在詠唱（`.chanting == False`）的話是 `(-1, -1)`。
        """
        return self.__teleport_destination

    @property
    def teleport_after(self) -> int:
        """
        多少 tick 以後會傳送到詠唱中的目標，如果沒有在詠唱（`.chanting == False`）的話是 `-1`。
        """
        return self.__teleport_after

    @property
    def teleport_cooldown_remain(self) -> int:
        """
        下一次可以開始詠唱的時間是多少 tick 以後。
        """
        return self.__teleport_cooldown_remain


class Patronus:
    """
    玩家獲得護法道具後召喚出的護法。
    """
    def __init__(self, _id: int, _position: Vector2, _owner: int):
        self.__id = _id
        self.__position = _position.copy()
        self.__owner = _owner

    @property
    def id(self) -> int:
        """
        護法編號，整場遊戲中出現的每一個護法都有不同編號。
        """
        return self.__id

    @property
    def position(self) -> int:
        """
        護法位置。
        """
        return self.__position

    @property
    def owner(self) -> int:
        """
        召喚出這個護法的玩家 ID。
        """
        return self.__owner


class Portkey:
    """
    港口鑰。
    """
    def __init__(self, _position: Vector2, _to: Vector2):
        self.__position = _position.copy()
        self.__to = _to.copy()

    @property
    def position(self) -> Vector2:
        """
        港口鑰位置。
        """
        return self.__position

    @property
    def to(self) -> Vector2:
        """
        傳送目標。
        """
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

    def get_time(self) -> int:
        pass

    def get_map_size(self) -> tuple[int, int]:
        pass

    def connected(self, a: Vector2, b: Vector2) -> bool:
        pass

    def connected_to(self, position: Vector2) -> bool:
        pass


_helper: Helper = None


def _set_helper(helper):
    global _helper
    _helper = helper


def get_items() -> list[Item]:
    """
    獲得目前在場上的所有道具。

    :returns: 包含場上所有道具的 `list`，保證這個 `list` 中的元素照道具的 ID 排序
    """
    return _helper.get_items()


def get_players() -> list[Player]:
    """
    獲得場上的所有玩家。

    :returns: 包含所有玩家的 `list`，保證這個 `list` 的長度是 4，
    且其中的元素照玩家 ID 排序。也就是說，`list` 裡第 `i` 個玩家的 ID 是 `i`
    """
    return _helper.get_players()


def get_ghosts() -> list[Ghost]:
    """
    獲得場上的所有鬼。

    :returns: 包含所有鬼的 `list`，保證這個 `list` 中的元素照鬼的 ID 排序。
    也就是說，`list` 裡第 `i` 個鬼的 ID 是 `i`
    """
    return _helper.get_ghosts()


def get_patronuses() -> list[Patronus]:
    """
    獲得場上的所有玩家召喚出的護法。

    :returns: 包含所有護法的 `list`，保證這個 `list` 中的元素照護法的 ID 排序
    """
    return _helper.get_patronuses()


def get_portkeys() -> list[Portkey]:
    """
    獲得所有港口鑰。

    :return: 包含所有港口鑰的 `list`
    """
    return _helper.get_portkeys()


def get_nearest_ghost() -> Ghost:
    """
    獲得距離自己位置（`get_myself().position`）最近的鬼。
    """
    return _helper.get_nearest_ghost()


def get_nearest_item() -> Item:
    """
    獲得距離自己位置（`get_myself().position`）最近的道具，如果場上沒有道具的話則是 `None`。
    """
    return _helper.get_nearest_item()


def get_nearest_player() -> Player:
    """
    `get_nearest_player() -> Player`：獲得距離自己位置（`get_myself().position`）最近的除了自己之外的玩家。
    """
    return _helper.get_nearest_player()


def get_ground_type(position: Vector2) -> GroundType:
    """
    獲得某個位置的地面類型。
    """
    return _helper.get_ground_type(position)


def get_myself() -> Player:
    """
    回傳代表自己的 `Player` 物件。
    """
    return _helper.get_myself()


def distance(a: Vector2, b: Vector2) -> float:
    """
    `a`、`b` 兩個位置之間的直線距離。
    """
    return _helper.distance(a, b)


def distance_to(position: Vector2) -> float:
    """
    自己的位置（`get_myself().position`）和 `position` 之間的直線距離。
    """
    return _helper.distance_to(position)


def get_time() -> int:
    """
    取得從遊戲開始到現在經過了幾個 tick。
    """
    return _helper.get_time()


def get_map_size() -> tuple[int, int]:
    """
    取得地圖大小。

    :return: 包含兩個 `int` 的 `tuple`，格式為 (width, height)，分別表示寬和高
    """
    return _helper.get_map_size()


def connected(a: Vector2, b: Vector2) -> bool:
    """
    兩個位置是否能不透過港口鑰互通。如果兩個位置有至少一個是障礙物，會回傳 False。
    """
    return _helper.connected(a, b)


def connected_to(position: Vector2) -> bool:
    """
    判斷一個位置是否能和目前所在位置互通。如果目標位置是障礙物，會回傳 False。
    """
    return _helper.connected_to(position)
