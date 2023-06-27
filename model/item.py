import math
import random

import numpy as np
import pygame as pg

import const
import utl
from instances_manager import get_game_engine


class Item:
    def __init__(self, position: pg.Vector2, item_id, item_type: const.ITEM_SET, item_width, item_height, item_status: const.ITEM_STATUS):
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
            if utl.overlaped(player.position, const.PLAYER_RADIUS, self.position, self.width):
                # Apply the effect to the player according to the type of item (item_type).
                player.get_effect(self.type, self.status)
                print(f"{player.player_id} get effect: {self.type} ({self.status})")
                return self  # which will be removed later in Model.py


class ItemGenerator:
    def __init__(self):
        model = get_game_engine()
        model.register_user_event(
            const.ITEM_GENERATE_COOLDOWN, self.generate_handler)
        model.register_user_event(
            const.GOLDEN_SNITCH_APPEAR_TIME,
            self.generate_golden_snitch)
        self.id_counter = 1

    def choose_location(self, candidates: list[pg.Vector2], objects: list[pg.Vector2]) -> pg.Vector2:
        """Return the location that is farthest to all objects among candidates"""
        best_location = pg.Vector2(0, 0)
        max_distance = 0
        model = get_game_engine()
        for candidate in candidates:
            # discard points not leggel
            if not (1 <= candidate.x <= const.ARENA_SIZE[0]
                    and 1 <= candidate.y <= const.ARENA_SIZE[1]
                    and model.map.get_type(candidate) == const.MAP_OBSTACLE):
                continue
            min_distance_to_objects = const.ARENA_SIZE[0] + const.ARENA_SIZE[1]
            for obj in objects:
                distance_to_object = math.hypot(obj.x - candidate.x, obj.y - candidate.y)
                min_distance_to_objects = min(min_distance_to_objects, distance_to_object)
            if min_distance_to_objects > max_distance:
                best_location = candidate
                max_distance = min_distance_to_objects
        return best_location

    def generate(self) -> bool:
        """
        Choose and try to generate a item at a location is far from all other items.

        Returns whether the attempt was successful.
        """
        # determining the type of generated item
        generate_type = random.choices(
            list(const.ITEM_SET), weights=const.ITEM_GENERATE_PROBABILITY)[0]
        generate_status = random.choices(
            list(const.ITEM_STATUS), weights=const.ITEM_STATUS_PROBABILITY)[0]

        # generate candidates of position
        rand_times = 12
        candidates_x = random.sample(range(const.ARENA_SIZE[0]), rand_times)
        candidates_y = random.sample(range(const.ARENA_SIZE[1]), rand_times)
        candidates = [pg.Vector2(x, y) for x, y in zip(candidates_x, candidates_y)]
        model = get_game_engine()
        items_position = [item.position for item in model.items]

        best = self.choose_location(candidates, items_position)
        if best == pg.Vector2(0, 0):
            print("Failed to generate item!")
            return False
        else:
            generate_item = Item(best, self.id_counter, generate_type,
                                 const.ITEM_WIDTH, const.ITEM_HEIGHT, generate_status)
            model.items.add(generate_item)
            self.id_counter = self.id_counter + 1
            print(f"Item {generate_type} generated at {best}!")
            return True

    def generate_handler(self):
        model = get_game_engine()
        try_again: int
        # if the number of item is less than MAX_ITEM_NUMBER, try to generate a item
        # else, wiat a rand time in the range [1, ITEM_GENERATE_COOLDOWN] and try again
        if len(model.items) < const.MAX_ITEM_NUMBER:
            # try to generate a item, and try again after 1 tick if the tempt failed
            if self.generate():
                try_again = const.ITEM_GENERATE_COOLDOWN
            else:
                try_again = 1
        else:
            try_again = random.randint(1, const.ITEM_GENERATE_COOLDOWN)
        model.register_user_event(try_again, self.generate_handler)

    def generate_golden_snitch(self):
        """Choose and generate golden snitch at a location is far from all players."""
        # randomly draw points in the arena according to a standard distribution
        rand_times = 12
        candidates_x = np.random.normal(
            const.ARENA_SIZE[0] / 2, const.ARENA_SIZE[0] / 4, rand_times)
        candidates_y = np.random.normal(
            const.ARENA_SIZE[1] / 2, const.ARENA_SIZE[1] / 4, rand_times)
        candidates = [pg.Vector2(x, y) for x, y in zip(candidates_x, candidates_y)]

        # choose the point that has a max distance to players
        model = get_game_engine()
        players_position = [player.position for player in model.players]
        best = self.choose_location(candidates, players_position)

        generate_item = Item(best, self.id_counter, const.ITEM_SET.GOLDEN_SNITCH,
                             const.ITEM_WIDTH, const.ITEM_HEIGHT, const.ITEM_STATUS.NORMAL)
        model.items.add(generate_item)
        self.id_counter = self.id_counter + 1
        print(f"Golden snitch generated at {best}!")
