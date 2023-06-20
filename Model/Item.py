from InstancesManager import get_game_engine

import math
import pygame as pg
import random
import Const

import numpy as np

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
                if self.status == "normal":
                    player.get_status(self.type, self.status)
    
    def __str__(self):
        return f"item_id: {self.item_id}, position: {self.position}"

class Item_Generator:
    def __init__(self):
        self.generate_cd = Const.ITEM_GENERATE_COOLDOWN
        self.id_counter = 1

    def generate(self):
        # determining the type of generated item
        generate_type = random.choices(Const.ITEM_SET, weights=Const.ITEM_GENERATE_PROBABILITY)[0]
        generate_status = random.choices(Const.ITEM_STATUS, weights=Const.ITEM_STATUS_PROBABILITY)[0]

        #determining location of item
        generate_x = 0
        generate_y = 0
        '''
        Put a random method to determine location here
        '''
        generate_item = Item(pg.Vector2(generate_x, generate_y), self.id_counter, generate_type, Const.ITEM_WIDTH, Const.ITEM_HEIGHT, generate_status)
        # print(generate_item)
        model = get_game_engine()
        model.items.append(generate_item)
        self.id_counter = self.id_counter + 1

    def tick(self):
        self.generate_cd -= 1
        model = get_game_engine()
        if model.timer == Const.GOLDEN_SNITCH_APPEAR_TIME:
            self.generate_golden_snitch()
        if self.generate_cd <= 0:
            if len(model.items) < Const.MAX_ITEM_NUMBER:
                self.generate()
                self.generate_cd = Const.ITEM_GENERATE_COOLDOWN
    
    def generate_golden_snitch(self):
        # find a position that is far from all the players
        max_distance = 0
        generate_x = 0
        generate_y = 0
        # randomly draw five points in the arena according to a standard distribution
        rand_times = 10
        candidates_x = np.random.normal(Const.WINDOW_SIZE[0] / 2, Const.WINDOW_SIZE[0] / 4, rand_times)
        candidates_y = np.random.normal(Const.WINDOW_SIZE[1] / 2, Const.WINDOW_SIZE[1] / 4, rand_times)
        model = get_game_engine()
        # choose the point that has a max distance to players
        for rand_x, rand_y in zip(candidates_x, candidates_y):
            # discard points out of range
            if not(1 <= rand_x <= Const.WINDOW_SIZE[0] and 1 <= rand_y <= Const.WINDOW_SIZE[1]):
                continue
            min_distance_to_players = Const.WINDOW_SIZE[0] + Const.WINDOW_SIZE[1]
            for player in model.players:
                distance_to_player = math.hypot(player.position.x - rand_x, player.position.y - rand_y)
                min_distance_to_players = min(min_distance_to_players, distance_to_player)
            if min_distance_to_players > max_distance:
                generate_x = rand_x
                generate_y = rand_y
                max_distance = min_distance_to_players
        generate_item = Item(pg.Vector2(generate_x, generate_y), self.id_counter, "golden_snitch", Const.ITEM_WIDTH, Const.ITEM_HEIGHT, "normal")
        model.items.append(generate_item)
        self.id_counter = self.id_counter + 1
        print(f"golden snitch generated at {generate_x, generate_y}!")
        print(generate_item)
