import random

import numpy as np
import pygame as pg

import const
import util
from event_manager.events import EventCastPetrification
from instances_manager import get_event_manager, get_game_engine


class Item:
    def __init__(self, position: pg.Vector2, item_id, item_type: const.ItemType):
        self.item_id = item_id
        self.type = item_type
        self.position = position
        self.eaten = False
        self.golden_snitch_goal = None
        self.vanish_time = get_game_engine().timer + const.ITEM_LIFETIME[item_type]

    def __str__(self):
        return f"item_id: {self.item_id}, position: {self.position}"

    def move_golden_snitch(self):
        model = get_game_engine()

        def mindis():
            return min((player.position - self.position).length() for player in model.players)

        def getweight(pos: pg.Vector2):
            ret = (pos - pg.Vector2(const.ARENA_SIZE[0] / 2, const.ARENA_SIZE[1] / 2)).length() * 2
            dis = (pos - self.position).length()
            for player in model.players:
                vec1 = player.position - self.position
                vec2 = pos - self.position
                dot = vec1.dot(vec2)
                if dot > 0:
                    dot = 1
                else:
                    dot = -1
                if vec1.length() < 200:
                    ret += dot * (20000 / min(150, abs(vec1.cross(vec2)) / dis))

            return ret
        if self.golden_snitch_goal is None or mindis() < 100:
            pnts = [pg.Vector2(random.uniform(0, const.ARENA_SIZE[0]),
                               random.uniform(0, const.ARENA_SIZE[1])) for _ in range(50)]
            weights = [getweight(pos) for pos in pnts]
            self.golden_snitch_goal = pnts[weights.index(min(weights))]

        # print("weight", getweight(self.golden_snitch_goal))
        if (self.golden_snitch_goal - self.position).length() < const.GOLDEN_SNITCH_SPEED:
            new_position = self.golden_snitch_goal
            self.golden_snitch_goal = None
        else:
            new_position = (self.position
                            + ((self.golden_snitch_goal - self.position).normalize()
                               * const.GOLDEN_SNITCH_SPEED))
        # clamp
        new_position.x = util.clamp(new_position.x, 0, const.ARENA_SIZE[0] - 1)
        new_position.y = util.clamp(new_position.y, 0, const.ARENA_SIZE[1] - 1)

        # Update
        self.position = new_position

    def tick(self):
        model = get_game_engine()
        for player in model.players:
            if (util.overlaped(player.position, const.PLAYER_RADIUS, self.position, const.ITEM_RADIUS)
                    and not player.dead):
                # Apply the effect to the player according to the type of item (item_type).
                self.eaten = True
                if self.type == const.ItemType.GOLDEN_SNITCH:
                    player.set_golden_snitch_effect()
                elif self.type == const.ItemType.PETRIFICATION:
                    others = [x for x in model.players if x != player and not x.dead]
                    if len(others) == 0:
                        continue
                    victim = random.choice(others)
                    get_event_manager().post(EventCastPetrification(player, victim))
                    print(f'{player.player_id} cast petrification against {victim.player_id}')
                else:
                    for i in const.EffectType:
                        if i.name == self.type.name:
                            player.set_effect(i)
                            break
                    print(f"{player.player_id} got effect: {self.type}!")
        if self.type == const.ItemType.GOLDEN_SNITCH:
            self.move_golden_snitch()


class ItemGenerator:
    def __init__(self):
        model = get_game_engine()
        model.register_user_event(const.ITEM_GENERATE_COOLDOWN, self.generate_handler)
        model.register_user_event(const.GOLDEN_SNITCH_APPEAR_TIME, self.generate_golden_snitch)
        self.id_counter = 1

    def choose_location(self, candidates: list[pg.Vector2], objects: list[pg.Vector2]) -> pg.Vector2:
        """Return the location that is farthest to all objects among candidates"""
        best_location = pg.Vector2(0, 0)
        max_distance = 0
        model = get_game_engine()
        for candidate in candidates:
            # discard points not leggel
            if not (const.ITEM_RADIUS < candidate.x < const.ARENA_SIZE[0] - const.ITEM_RADIUS
                    and const.ITEM_RADIUS < candidate.y < const.ARENA_SIZE[1] - const.ITEM_RADIUS) \
                    or model.map.get_type(candidate) == const.MAP_OBSTACLE:
                continue
            min_distance_to_objects = const.ARENA_SIZE[0] + const.ARENA_SIZE[1]
            for obj in objects:
                distance_to_object = obj.distance_to(candidate)
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
            list(const.ItemType), weights=const.ITEM_GENERATE_PROBABILITY)[0]

        # generate candidates of position
        rand_times = 15
        candidates_x = random.sample(
            range(const.ITEM_RADIUS, const.ARENA_SIZE[0] - 1 - const.ITEM_RADIUS), rand_times)
        candidates_y = random.sample(
            range(const.ITEM_RADIUS, const.ARENA_SIZE[1] - 1 - const.ITEM_RADIUS), rand_times)
        candidates = [pg.Vector2(x, y) for x, y in zip(candidates_x, candidates_y)]
        model = get_game_engine()
        items_position = [item.position for item in model.items]

        best = self.choose_location(candidates, items_position)
        too_close = False
        for player in model.players:
            too_close = True if too_close or best.distance_to(player.position) < 150 else False
        if best == pg.Vector2(0, 0) or too_close:
            # print("Failed to generate item!")
            return False
        else:
            generate_item = Item(best, self.id_counter, generate_type)
            model.items.add(generate_item)
            self.id_counter = self.id_counter + 1
            # print(f"Item {generate_type} generated at {best}!")
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
        rand_times = 15
        candidates_x = np.random.normal(
            const.ARENA_SIZE[0] / 2, const.ARENA_SIZE[0] / 4, rand_times)
        candidates_y = np.random.normal(
            const.ARENA_SIZE[1] / 2, const.ARENA_SIZE[1] / 4, rand_times)
        candidates = [pg.Vector2(x, y) for x, y in zip(candidates_x, candidates_y)]

        # choose the point that has a max distance to players
        model = get_game_engine()
        players_position = [player.position for player in model.players]
        best = self.choose_location(candidates, players_position)

        generate_item = Item(best, self.id_counter, const.ItemType.GOLDEN_SNITCH)
        model.items.add(generate_item)
        self.id_counter = self.id_counter + 1
        # print(f"Golden snitch generated at {best}!")
