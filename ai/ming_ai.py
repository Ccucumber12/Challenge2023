from api.api import *

import pygame as pg
import random


class TeamAI(AI):

    def __init__(self):
        self.destination = None

    def player_tick(self) -> Vector2:
        center = pg.Vector2(600, 400)
        tforce = pg.Vector2(0, 0)
        myself = get_myself()

        def gforce(a: pg.Vector2, b: pg.Vector2):
            if a == b:
                return pg.Vector2(0, 0)
            length = (b - a).length()
            return (b - a).normalize() / (length ** 2)
        
        for player in get_players():
            if player == myself:
                continue
            G = -1
            if player.dead:
                G = -0.2
            if myself.dead:
                G = -0.1
            if player.position != myself.position:
                tforce += G*gforce(myself.position, player.position)
        for ghost in get_ghosts():
            if myself.effect == EffectType.SORTINGHAT:
                G = 4
            if myself.dead or myself.effect == EffectType.CLOAK:
                G = -0.5
            else:
                G = -1
            if ghost.position != myself.position:
                tforce += G*gforce(myself.position, ghost.position)
        # for item in get_items():
        #     if item.position != myself.position:
        #         if item.type == ItemType.CLOAK:
        #             G = 5
        #         if item.type == ItemType.GOLDEN_SNITCH:
        #             G = 1
        #         if item.type == ItemType.PATRONUS:
        #             G = 3
        #         if item.type == ItemType.PETRIFICATION:
        #             G = 4
        #         if item.type == ItemType.SORTINGHAT:
        #             G = 8
        #         tforce += G*gforce(myself.position, item.position)

        G = 0.3
        tforce += G*gforce(myself.position, (0, 0))
        tforce += G*gforce(myself.position, (1200, 0))
        tforce += G*gforce(myself.position, (0, 800))
        tforce += G*gforce(myself.position, (1200, 800))

        # print(tforce.length())

        if self.destination is not None:
            if (self.destination-myself.position).length() < myself.speed:
                self.destination = None
        if tforce.length() > 2.3e-05:
            if get_ground_type(myself.position + tforce.normalize()*3) != GroundType.OBSTACLE:
                self.destination = None
                return myself.position + tforce.normalize()*3
        if self.destination is None:
            if get_nearest_item() is not None:
                self.destination = get_nearest_item().position
                return self.destination
            self.destination = pg.Vector2(random.randint(0, 1199), random.randint(0, 799))
            while get_ground_type(self.destination) == GroundType.OBSTACLE:
                self.destination = pg.Vector2(random.randint(0, 1199), random.randint(0, 799))
        return self.destination