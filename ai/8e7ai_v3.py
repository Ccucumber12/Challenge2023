from pygame import Vector2

from api.api import *
import random
import math


class TeamAI(AI):

    def __init__(self):
        tmp = [Vector2(random.uniform(0, 1200), random.uniform(0, 800)) for i in range(300)]
        self.candidates = []
        for i in tmp:
            if get_ground_type(i) != GroundType.OBSTACLE:
                self.candidates.append(i)
         
    def evaluate_position(self, pos):
        #tries to find the most "empty" position that is nearby
        ghosts = get_ghosts()
        #ret = math.sqrt(distance(pos, get_myself().position)) * 2
        ret = 0
        if get_ground_type(pos) == GroundType.OBSTACLE:
            ret += 10000
        for ghost in ghosts:
            dis = distance(ghost.position, pos)
            ret -= min(400, dis) - min(150, dis)
        #ret -= distance(get_myself().position, get_nearest_player().position)
        return ret
    
    def evaluate_items(self, item):
        #evaluates the value of an item
        ret = 0
        if item.type == ItemType.GOLDEN_SNITCH:
            if get_myself().effect == EffectType.CLOAK: 
                return -10000
            else:
                return 10000
        elif item.type == ItemType.CLOAK:
            #no golden snitch strat
            has_golden_snitch = False
            for i in get_items():
                if i.type == ItemType.GOLDEN_SNITCH:
                    has_golden_snitch = True
            dis = distance(item.position, get_myself().position)
            if has_golden_snitch: 
                if dis < 500:
                    return dis * 0.1
                else:
                    return dis * 0.3
            else:
                return distance(item.position, get_myself().position) * 0.8
        elif item.type == ItemType.PATRONUS:
            return distance(item.position, get_myself().position)
        elif item.type == ItemType.PETRIFICATION:
            multi = 1
            for i in get_players(): 
                if i != get_myself() and i.effect != EffectType.NONE:
                    multi -= 0.2
            return distance(item.position, get_myself().position) * multi
        else:
            #Sorting hat
            ret = distance(item.position, get_myself().position) * 0.25
            ret += min(distance(ghost.position, item.position) for ghost in get_ghosts()) * 0.1
            return ret

    def player_tick(self) -> Vector2:
        pos = get_myself().position
        vec = get_nearest_ghost().position - pos

        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
        for i in get_items():
            if i.type == ItemType.GOLDEN_SNITCH:
                has_golden_snitch = True
                golden_snitch_pos = i.position

        items = get_items()
        items.sort(key=lambda x: self.evaluate_items(x))
        if get_myself().effect == EffectType.SORTINGHAT:
            return pos + vec
        if has_golden_snitch and get_myself().effect == EffectType.CLOAK:
            return golden_snitch_pos
        
        if len(items) > 0 and (distance(items[0].position, pos) < max(vec.length(), 150) or vec.length() > 350 or get_myself().dead):
            return items[0].position
        else:
            ret = min(self.candidates,
                key=lambda x: self.evaluate_position(x),
                default=None)
            return ret
