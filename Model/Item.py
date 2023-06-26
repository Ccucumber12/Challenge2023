import math
import random

import numpy as np
import pygame as pg

import Const
from InstancesManager import get_game_engine


class Item:
    def __init__(self, position, item_id, item_type, item_width, item_height, item_status):
        self.item_id = item_id
        self.type = item_type
        # specify the type of item ["cloak": 隱形斗篷, "patronus": 護法, "golden_snitch": 金探子, "petrification": 石化]
        self.position = position  # is a pg.Vector2
        self.width = item_width
        self.height = item_height
        self.status = item_status  # ["normal", "reversed", "enhanced"]

    def tick(self):
        model = get_game_engine()
        for player in model.players:
            if self.position.x - (self.width / 2) <= player.position.x <= self.position.x + (self.width / 2) and \
                    self.position.y - (self.height / 2) <= player.position.y <= self.position.y + (self.height / 2):
                '''
                Apply the effect to the player according to the type of item (item_type).
                '''
                print(f"{player.player_id} get effect: {self.type} ({self.status})")
                player.get_effect(self.type, self.status)
                return self # which will be removed later in Model.py

    def __str__(self):
        return f"item_id: {self.item_id}, position: {self.position}"


class Item_Generator:
    def __init__(self):
        model = get_game_engine()
        model.register_user_event(Const.ITEM_GENERATE_COOLDOWN, self.generate_handler)
        model.register_user_event(Const.GOLDEN_SNITCH_APPEAR_TIME, self.generate_golden_snitch)
        self.id_counter = 1

    def generate(self):
        # determining the type of generated item
        generate_type = random.choices(list(Const.ITEM_SET), weights=Const.ITEM_GENERATE_PROBABILITY)[0]
        generate_status = random.choices(list(Const.ITEM_STATUS), weights=Const.ITEM_STATUS_PROBABILITY)[0]

        # determining location of item
        generate_x = 0
        generate_y = 0
        generate_x = random.random() * 800 - 1
        generate_y = random.random() * 800 - 1
        '''
        Put a random method to determine location here
        '''
        generate_item = Item(pg.Vector2(generate_x, generate_y), self.id_counter, generate_type, Const.ITEM_WIDTH, Const.ITEM_HEIGHT, generate_status)
        # print(generate_item)
        model = get_game_engine()
        model.items.add(generate_item)
        self.id_counter = self.id_counter + 1
        print(f"Item {generate_type} generated at {generate_x, generate_y}!")

    def generate_handler(self):
        model = get_game_engine()
        if len(model.items) < Const.MAX_ITEM_NUMBER:
            self.generate()
            model.register_user_event(Const.ITEM_GENERATE_COOLDOWN, self.generate_handler)
        else:
            model.register_user_event(1, self.generate_handler)

    def tick(self):
        pass

    def generate_golden_snitch(self):
        # find a position that is far from all the players
        max_distance = 0
        generate_x = 0
        generate_y = 0
        # randomly draw points in the arena according to a standard distribution
        rand_times = 10
        candidates_x = np.random.normal(Const.ARENA_SIZE[0] / 2, Const.ARENA_SIZE[0] / 4, rand_times)
        candidates_y = np.random.normal(Const.ARENA_SIZE[1] / 2, Const.ARENA_SIZE[1] / 4, rand_times)
        model = get_game_engine()
        # choose the point that has a max distance to players
        for rand_x, rand_y in zip(candidates_x, candidates_y):
            # discard points out of range
            if not(1 <= rand_x <= Const.ARENA_SIZE[0] and 1 <= rand_y <= Const.ARENA_SIZE[1]):
                continue
            min_distance_to_players = Const.ARENA_SIZE[0] + Const.ARENA_SIZE[1]
            for player in model.players:
                distance_to_player = math.hypot(player.position.x - rand_x, player.position.y - rand_y)
                min_distance_to_players = min(min_distance_to_players, distance_to_player)
            if min_distance_to_players > max_distance:
                generate_x = rand_x
                generate_y = rand_y
                max_distance = min_distance_to_players
        generate_item = Item(pg.Vector2(generate_x, generate_y), self.id_counter, Const.ITEM_SET.GOLDEN_SNITCH, Const.ITEM_WIDTH, Const.ITEM_HEIGHT, Const.ITEM_STATUS.NORMAL)
        model.items.add(generate_item)
        self.id_counter = self.id_counter + 1
        print(f"Golden snitch generated at {generate_x, generate_y}!")
        print(generate_item)
