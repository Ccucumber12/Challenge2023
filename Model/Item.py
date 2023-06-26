import math
import random

import numpy as np
import pygame as pg

import Const
from InstancesManager import get_game_engine
import Utl


class Item:
    def __init__(self, position: pg.Vector2, item_id, item_type, item_width, item_height, item_status: Const.ITEM_STATUS):
        self.item_id = item_id
        self.type = item_type
        self.position = position
        self.width = item_width
        self.height = item_height
        self.status = item_status

    def __str__(self):
        return f"item_id: {self.item_id}, position: {self.position}"

    def tick(self):
        model = get_game_engine()
        for player in model.players:
            if Utl.overlaped(player.position, Const.PLAYER_RADIUS, self.position, self.width):
                '''
                Apply the effect to the player according to the type of item (item_type).
                '''
                print(f"{player.player_id} get effect: {self.type} ({self.status})")
                player.get_effect(self.type, self.status)
                return self  # which will be removed later in Model.py


class ItemGenerator:
    def __init__(self):
        model = get_game_engine()
        model.register_user_event(
            Const.ITEM_GENERATE_COOLDOWN, self.generate_handler)
        model.register_user_event(
            Const.GOLDEN_SNITCH_APPEAR_TIME, self.generate_golden_snitch)
        self.id_counter = 1

    def choose_location(self, condidates: list[pg.Vector2], objects: list[pg.Vector2]) -> pg.Vector2:
        best_location = pg.Vector2(0, 0)
        max_distance = 0
        for candidate in condidates:
            # discard points out of range.
            if not (1 <= candidate.x <= Const.ARENA_SIZE[0] and 1 <= candidate.y <= Const.ARENA_SIZE[1]):
                continue
            min_distance_to_objects = Const.ARENA_SIZE[0] + Const.ARENA_SIZE[1]
            for object in objects:
                distance_to_object = math.hypot(
                    object.x - candidate.x, object.y - candidate.y)
                min_distance_to_objects = min(
                    min_distance_to_objects, distance_to_object)
            if min_distance_to_objects > max_distance:
                best_location = candidate
                max_distance = min_distance_to_objects
        return best_location

    def generate(self):
        # determining the type of generated item
        generate_type = random.choices(
            list(Const.ITEM_SET), weights=Const.ITEM_GENERATE_PROBABILITY)[0]
        generate_status = random.choices(
            list(Const.ITEM_STATUS), weights=Const.ITEM_STATUS_PROBABILITY)[0]

        # determining location of item

        generate_x = random.randint(0, Const.ARENA_SIZE[0])
        generate_y = random.randint(0, Const.ARENA_SIZE[1])
        model = get_game_engine()
        while model.map.get_type(pg.Vector2(generate_x, generate_y)) == Const.MAP_OBSTACLE:
            generate_x = random.randint(0, Const.ARENA_SIZE[0])
            generate_y = random.randint(0, Const.ARENA_SIZE[1])

        generate_item = Item(pg.Vector2(generate_x, generate_y), self.id_counter,
                             generate_type, Const.ITEM_WIDTH, Const.ITEM_HEIGHT, generate_status)
        model = get_game_engine()
        model.items.add(generate_item)
        self.id_counter = self.id_counter + 1
        print(f"Item {generate_type} generated at {generate_x, generate_y}!")

    def generate_handler(self):
        model = get_game_engine()
        if len(model.items) < Const.MAX_ITEM_NUMBER:
            self.generate()
            model.register_user_event(
                Const.ITEM_GENERATE_COOLDOWN, self.generate_handler)
        else:
            model.register_user_event(1, self.generate_handler)

    def generate_golden_snitch(self):
        # find a position that is far from all the players
        max_distance = 0
        generate_x = 0
        generate_y = 0

        # randomly draw points in the arena according to a standard distribution
        rand_times = 10
        candidates_x = np.random.normal(
            Const.ARENA_SIZE[0] / 2, Const.ARENA_SIZE[0] / 4, rand_times)
        candidates_y = np.random.normal(
            Const.ARENA_SIZE[1] / 2, Const.ARENA_SIZE[1] / 4, rand_times)
        candidates = [pg.Vector2(x, y)
                      for x, y in zip(candidates_x, candidates_y)]

        # choose the point that has a max distance to players
        model = get_game_engine()
        players_position = [player.position for player in model.players]
        best = self.choose_location(candidates, players_position)

        generate_item = Item(best, self.id_counter, Const.ITEM_SET.GOLDEN_SNITCH,
                             Const.ITEM_WIDTH, Const.ITEM_HEIGHT, Const.ITEM_STATUS.NORMAL)
        model.items.add(generate_item)
        self.id_counter = self.id_counter + 1
        print(f"Golden snitch generated at {generate_x, generate_y}!")
