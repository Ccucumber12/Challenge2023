from pygame import Vector2

from api.api import *
import random


class TeamAI(AI):

    def evaluate_position(self, pos):
        #tries to find the most "empty" position that is nearby
        ghosts = get_ghosts()
        ret = distance(pos, get_myself().position)
        if get_ground_type(pos) == GroundType.OBSTACLE:
            ret += 10000
        for ghost in ghosts:
            ret -= distance(ghost.position, get_myself().position)
        ret -= distance(get_myself().position, get_nearest_player().position)
        return ret
    
    def evaluate_items(self, item):
        #evaluates the value of an item
        ret = 0
        if item.type == ItemType.GOLDEN_SNITCH:
            if get_myself().effect == EffectType.CLOAK: 
                return 10000
            else:
                return -10000
        elif item.type == ItemType.CLOAK:
            #no golden snitch strat
            ret = sum(distance(ghost.position, item.position) for ghost in get_ghosts()) / len(get_ghosts()) * 0.8
            return ret 
        elif item.type == ItemType.PATRONUS:
            return distance(item.position, get_myself().position)
        elif item.type == ItemType.PETRIFICATION:
            return distance(item.position, get_myself().position)
        else:
            #Sorting hat
            return distance(item.position, get_myself().position) * 0.4

    def player_tick(self) -> Vector2:
        pos = get_myself().position
        vec = get_nearest_ghost().position - pos
        items = get_items()
        items.sort(key=lambda x: self.evaluate_items(x))
        if get_myself().effect == EffectType.SORTINGHAT:
            return pos + vec
        if vec.length() < 200:
            return pos - vec
        if get_nearest_item() is not None:
            if ItemType.GOLDEN_SNITCH in items:
                #print("Has golden snitch")
                for i in items:
                    if i.type == ItemType.CLOAK:
                        return i.position
            else:
                for i in items:
                    if i.type == ItemType.SORTINGHAT:
                        return i.position
            return get_nearest_item().position
        else:
            candidates = [Vector2(random.uniform(0, 1200), random.uniform(0, 800)) for i in range(10)] 
            ret = min(candidates,
                key=lambda x: self.evaluate_position(x),
                default=None)
            return ret

