import importlib
import platform
import signal
import threading
import traceback

from pygame import Vector2

import const
import error
import instances_manager
import util
from api.api import (EffectType, Ghost, GroundType, Helper, Item, ItemType, Patronus, Player,
                     Portkey, SortKey, _set_helper)
from event_manager.events import EventPlayerMove


class HelperImpl(Helper):

    def __init__(self):
        self._current_player = -1

    @staticmethod
    def __check_position(v, function_name, variable_name):
        if type(v) is tuple:
            v = Vector2(v)
        if type(v) is not Vector2:
            raise TypeError(f'{function_name}: {variable_name} is neither Vector2 nor tuple')
        return v

    @staticmethod
    def __check_sort_key(v, function_name, variable_name='sort_key'):
        if type(v) is not SortKey:
            raise TypeError(f'{function_name}: {variable_name} is not SortKey')

    def __sort_list(self, sort_key, t: list, function_name):
        HelperImpl.__check_sort_key(sort_key, function_name)
        if sort_key == SortKey.DISTANCE:
            t.sort(key=lambda v: self.distance_to(v.position))

    def get_items(self, sort_key: SortKey = SortKey.ID) -> list[Item]:
        model = instances_manager.get_game_engine()
        items = [Item(i.item_id,
                      ItemType.get_by_name(i.type.name),
                      i.position)
                 for i in model.items]
        self.__sort_list(sort_key, items, 'get_items')
        return items

    def get_players(self, sort_key: SortKey = SortKey.ID) -> list[Player]:
        model = instances_manager.get_game_engine()
        players = [Player(int(i.player_id),
                          i.position,
                          i.dead,
                          i.respawn_time - model.timer if i.dead else -1,
                          i.speed,
                          i.score,
                          EffectType.NONE if i.effect is None else EffectType.get_by_name(
                              i.effect.name),
                          i.effect_timer,
                          i.golden_snitch)
                   for i in model.players]
        self.__sort_list(sort_key, players, 'get_players')
        return players

    def get_ghosts(self, sort_key: SortKey = SortKey.ID) -> list[Ghost]:
        model = instances_manager.get_game_engine()
        ghosts = []
        for i in model.ghosts:
            destination = i.teleport_destination if i.teleport_chanting else Vector2(-1, -1)
            after = i.teleport_after if i.teleport_chanting else -1
            cooldown = i.teleport_cooldown_remain
            ghost = Ghost(i.ghost_id,
                          i.position,
                          i.speed,
                          i.teleport_chanting,
                          destination,
                          after,
                          cooldown)
            ghosts.append(ghost)
        self.__sort_list(sort_key, ghosts, 'get_ghosts')
        return ghosts

    def get_patronuses(self, sort_key: SortKey = SortKey.ID) -> list[Patronus]:
        model = instances_manager.get_game_engine()
        patronuses = [Patronus(i.patronus_id,
                               i.position,
                               i.speed,
                               i.owner.player_id)
                      for i in model.patronuses]
        self.__sort_list(sort_key, patronuses, 'get_patronuses')
        return patronuses

    def get_portkeys(self, sort_key: SortKey = SortKey.ID) -> list[Portkey]:
        model = instances_manager.get_game_engine()
        map_obj = model.map
        portkeys = [Portkey(i,
                            map_obj.convert_cell(portal[0]),
                            map_obj.convert_cell(portal[1]))
                    for i, portal in zip(range(len(map_obj.portals)), map_obj.portals)]
        self.__sort_list(sort_key, portkeys, 'get_portkeys')
        return portkeys

    def get_nearest_ghost(self) -> Ghost:
        ghosts = self.get_ghosts()
        nearest = None
        dis = float('nan')
        for i in ghosts:
            if nearest is None or self.distance_to(i.position) < dis:
                dis = self.distance_to(i.position)
                nearest = i
        return nearest

    def get_nearest_item(self) -> Item:
        items = self.get_items()
        nearest = None
        dis = float('nan')
        for i in items:
            if nearest is None or self.distance_to(i.position) < dis:
                dis = self.distance_to(i.position)
                nearest = i
        return nearest

    def get_nearest_player(self) -> Player:
        players = self.get_players()
        nearest = None
        dis = float('nan')
        for i in players:
            if i.id == self._current_player:
                continue
            if nearest is None or self.distance_to(i.position) < dis:
                dis = self.distance_to(i.position)
                nearest = i
        return nearest

    def get_ground_type(self, position: Vector2 | tuple[float, float]) -> GroundType:
        position = self.__check_position(position, 'get_ground_type', 'position')
        model = instances_manager.get_game_engine()
        return GroundType.get_by_num(model.map.get_type(position))

    def get_myself(self) -> Player:
        return self.get_players()[self._current_player]

    def distance(self, a: Vector2 | tuple[float, float], b: Vector2 | tuple[float, float]) -> float:
        a = self.__check_position(a, 'distance', 'a')
        b = self.__check_position(b, 'distance', 'b')
        return a.distance_to(b)

    def distance_to(self, position: Vector2 | tuple[float, float]) -> float:
        position = self.__check_position(position, 'distance_to', 'position')
        return self.distance(self.get_myself().position, position)

    def get_time(self) -> int:
        model = instances_manager.get_game_engine()
        return model.timer

    def get_map_size(self) -> tuple[int, int]:
        return const.ARENA_SIZE

    def connected(self, a: Vector2 | tuple[float, float], b: Vector2 | tuple[float, float]) -> bool:
        a = self.__check_position(a, 'connected', 'a')
        b = self.__check_position(b, 'connected', 'b')
        model = instances_manager.get_game_engine()
        return model.map.in_same_connected_component(a, b)

    def connected_to(self, position: Vector2 | tuple[float, float]) -> bool:
        position = self.__check_position(position, 'connected_to', 'position')
        return self.connected(self.get_myself().position, position)

    def get_map_name(self) -> str:
        model = instances_manager.get_game_engine()
        return model.map.name

    def find_possible_portkeys(self, source: Vector2 | tuple[float, float],
                               target: Vector2 | tuple[float, float],
                               sort_key: SortKey = SortKey.ID) -> list[Portkey]:
        source = HelperImpl.__check_position(source, 'find_possible_portkeys', 'source')
        target = HelperImpl.__check_position(target, 'find_possible_portkeys', 'target')
        candidates = []
        for i in self.get_portkeys():
            if self.connected(source, i.position) and self.connected(target, i.target):
                candidates.append(i)
        self.__sort_list(sort_key, candidates, 'find_possible_portkeys')
        return candidates

    def find_possible_portkeys_to(self, target: Vector2 | tuple[float, float],
                                  sort_key: SortKey = SortKey.ID) -> list[Portkey]:
        target = HelperImpl.__check_position(target, 'find_possible_portkeys_to', 'target')
        self.__check_sort_key(sort_key, 'find_possible_portkeys_to')
        return self.find_possible_portkeys(self.get_myself().position, target)

    def get_reachable_portkeys(self, sort_key: SortKey = SortKey.ID) -> list[Portkey]:
        portkeys = []
        for i in self.get_portkeys():
            if self.connected_to(i.position):
                portkeys.append(i)
        self.__sort_list(sort_key, portkeys, 'get_reachable_portkeys')
        return portkeys

    def get_ticks_per_second(self) -> int:
        return const.FPS


__helper_impl = HelperImpl()
__ai = [None] * 4
__last_target = [None] * 4


def get_last_target(player_id):
    return __last_target[player_id]


class Timer():
    def __init__(self):
        self.system = platform.system()
        if self.system != 'Windows':
            def handler(sig, frame):
                raise error.TimeoutError()

            signal.signal(signal.SIGALRM, handler)
        self.timer = None
        self.for_player_id = None

    def set_timer(self, interval: float, player_id: int):
        if self.system != 'Windows':
            signal.setitimer(signal.ITIMER_REAL, interval)
        else:
            def timeout_alarm(player_id: int):
                print(f"The AI of player {player_id} time out!")

            self.timer = threading.Timer(interval=interval, function=timeout_alarm,
                                         args=[player_id])
            self.timer.start()

    def cancel_timer(self):
        if self.system != 'Windows':
            signal.setitimer(signal.ITIMER_REAL, 0)
        else:
            self.timer.cancel()


def init(ai_file):
    global __ai
    global __timer
    __timer = Timer()
    _set_helper(__helper_impl)
    model = instances_manager.get_game_engine()
    for i in const.PlayerIds:
        if ai_file[i] == 'manual':
            continue
        file = 'ai.' + ai_file[i]
        try:
            __timer.set_timer(1, i)
            m = importlib.import_module(file)
            __ai[i] = m.TeamAI()
            __timer.cancel_timer()
        except Exception as e:
            __timer.cancel_timer()
            print(f"Exception in ai of player {i}.")
            if model.no_error_message:
                print(f'{util.get_full_exception(e)}: {e}')
            else:
                print(traceback.format_exc())
            raise


def call_ai(player_id: int):
    __last_target[player_id] = None
    model = instances_manager.get_game_engine()
    if __ai[player_id] is None:
        return
    __helper_impl._current_player = player_id
    try:
        __timer.set_timer(1 / (5 * const.FPS), player_id)
        destination = __ai[player_id].player_tick()
        __timer.cancel_timer()
        if type(destination) != Vector2:
            raise error.WrongTypeError()
    except Exception as e:
        __timer.cancel_timer()
        print(f"Exception in ai of player {player_id}.")
        if model.no_error_message:
            print(f'{util.get_full_exception(e)}: {e}')
        else:
            print(traceback.format_exc())
        return
    __last_target[player_id] = destination
    player = model.players[player_id]
    event_manager = instances_manager.get_event_manager()
    event_manager.post(
        EventPlayerMove(player_id, Vector2(player.pathfind(*destination)) - player.position))
