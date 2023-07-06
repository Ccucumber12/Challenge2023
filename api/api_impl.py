import importlib

import pygame as pg
from pygame import Vector2

import instances_manager
from api.api import AI, Ghost, GroundType, Helper, Item, ItemType, Player, _set_helper, Patronus, Portkey
from event_manager.events import EventPlayerMove


class HelperImpl(Helper):

    def __init__(self):
        self._current_player = -1

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
                          i.speed,
                          i.score,
                          None if i.effect is None else ItemType.get_by_name(i.effect.name),
                          i.effect_timer)
                   for i in model.players]
        return players

    def get_ghosts(self) -> list[Ghost]:
        model = instances_manager.get_game_engine()
        ghosts = []
        for i in model.ghosts:
            destination = i.teleport_distination if i.teleport_chanting else None
            after = i.teleport_after if i.teleport_chanting else None
            cooldown = i.teleport_cooldown_remain
            ghost = Ghost(i.ghost_id,
                          i.position,
                          i.speed,
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

    def get_ground_type(self, position: Vector2) -> GroundType:
        model = instances_manager.get_game_engine()
        return GroundType.get_by_num(model.map.get_type(position))

    def get_myself(self) -> Player:
        return self.get_players()[self._current_player]

    def distance(self, a: Vector2, b: Vector2) -> float:
        return a.distance_to(b)

    def distance_to(self, position: Vector2) -> float:
        return self.distance(self.get_myself().position, position)


__helper_impl = HelperImpl()
__ai = [None] * 4


def init(ai_file):
    global __ai
    _set_helper(__helper_impl)
    for i in range(0, 4):
        if ai_file[i] == 'manual':
            continue
        file = ai_file[i]
        m = importlib.import_module(file)
        __ai[i] = m.TeamAI()


def call_ai(player_id):
    if __ai[player_id] is None:
        return
    __helper_impl._current_player = player_id
    destination = __ai[player_id].player_tick()
    model = instances_manager.get_game_engine()
    player = model.players[player_id]
    event_manager = instances_manager.get_event_manager()
    event_manager.post(EventPlayerMove(player_id, pg.Vector2(player.pathfind(*destination)) - player.position))
