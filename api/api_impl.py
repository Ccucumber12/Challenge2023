import importlib
import threading

import pygame as pg
from pygame import Vector2

import const
import instances_manager
from api.api import (EffectType, Ghost, GroundType, Helper, Item, ItemType, Patronus, Player,
                     Portkey, _set_helper)
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

    def get_items(self) -> list[Item]:
        model = instances_manager.get_game_engine()
        items = [Item(i.item_id,
                      ItemType.get_by_name(i.type.name),
                      i.position)
                 for i in model.items]
        return items

    def get_players(self) -> list[Player]:
        model = instances_manager.get_game_engine()
        players = [Player(i.player_id,
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
        return players

    def get_ghosts(self) -> list[Ghost]:
        model = instances_manager.get_game_engine()
        ghosts = []
        for i in model.ghosts:
            destination = i.teleport_distination if i.teleport_chanting else Vector2(-1, -1)
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
        return ghosts

    def get_patronuses(self) -> list[Patronus]:
        model = instances_manager.get_game_engine()
        patronuses = [Patronus(i.patronus_id,
                               i.position,
                               i.owner.player_id)
                      for i in model.patronuses]
        return patronuses

    def get_portkeys(self) -> list[Portkey]:
        model = instances_manager.get_game_engine()
        map_obj = model.map
        portkeys = [Portkey(map_obj.convert_cell((i[0], i[1])),
                            map_obj.convert_cell((i[2], i[3])))
                    for i in map_obj.portals]
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


__helper_impl = HelperImpl()
__ai = [None] * 4


def init(ai_file):
    global __ai
    _set_helper(__helper_impl)
    for i in range(0, 4):
        if ai_file[i] == 'manual':
            continue
        file = 'ai.'+ ai_file[i]
        m = importlib.import_module(file)
        __ai[i] = m.TeamAI()


def call_ai(player_id):
    def timeout_alarm(player_id: int):
        print(f"The AI of player {player_id} time out!")
    if __ai[player_id] is None:
        return
    __helper_impl._current_player = player_id
    timer = threading.Timer(interval=1 / (6 * const.FPS), function=timeout_alarm, args=[player_id])
    timer.start()
    destination = __ai[player_id].player_tick()
    timer.cancel()
    model = instances_manager.get_game_engine()
    player = model.players[player_id]
    event_manager = instances_manager.get_event_manager()
    event_manager.post(
        EventPlayerMove(player_id, pg.Vector2(player.pathfind(*destination)) - player.position))
