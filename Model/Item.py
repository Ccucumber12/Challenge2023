from InstancesManager import get_game_engine

import pygame as pg
import random
import Const

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
        self.golden_snitch_tag = 0
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
        generate_x = 0
        generate_y = 0
        generate_item = Item(pg.Vector2(generate_x, generate_y), self.id_counter, "golden_snitch", Const.ITEM_WIDTH, Const.ITEM_HEIGHT, "normal")
        model = get_game_engine()
        model.items.append(generate_item)
        self.id_counter = self.id_counter + 1
        print("golden snitch generated!")
        print(generate_item)
