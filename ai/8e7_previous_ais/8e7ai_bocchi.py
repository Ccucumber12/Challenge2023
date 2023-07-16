from pygame import Vector2

from api.api import *
import random
import math

class TeamAI(AI):

    def __init__(self):
        self.candidates = []
        while len(self.candidates) < 100:
            i = Vector2(random.uniform(0, 1200), random.uniform(0, 800))
            if get_ground_type(i) != GroundType.OBSTACLE:
                self.candidates.append(i)
        self.portkey_eval = None
    
    def get_close_positions(self):
        return [pos for pos in self.candidates if distance(pos, get_myself().position) < 350] 
    def evaluate_position(self, pos):
        #tries to find the most "empty" position that is nearby
        portkey = False
        if not connected_to(pos):
            if self.portkey_eval is not None:
                return self.portkey_eval
            portkey = True
            pos = find_possible_portkeys_to(pos)[0].target
        ghosts = get_ghosts()
        players = get_players() 
        my_id = get_myself().id
        ret = 0
        if get_ground_type(pos) == GroundType.OBSTACLE:
            ret += 10000
        for ghost in ghosts:
            ghostpos = ghost.position
            if connected(pos, ghostpos):
                same_side = True
            if ghost.chanting: 
                ghostpos = ghost.teleport_destination
            dis = distance(ghostpos, pos)
            ret -= min(500, dis) + min(200, dis)
        for player in players:
            if player.id == my_id:
                continue
            ret -= distance(pos, player.position)
        if portkey:
            self.portkey_eval = ret
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
                ret = distance(item.position, get_myself().position) * 0.6
                ret += min(distance(ghost.position, item.position) for ghost in get_ghosts()) * 0.2
                return ret
        elif item.type == ItemType.PATRONUS:
            return distance(item.position, get_myself().position)
        elif item.type == ItemType.PETRIFICATION:
            multi = 1
            for i in get_players(): 
                if i != get_myself() and i.effect != EffectType.NONE:
                    multi -= 0.15
            return distance(item.position, get_myself().position) * multi
        else:
            #Sorting hat
            ret = distance(item.position, get_myself().position) * 0.2
            ret += min(distance(ghost.position, item.position) for ghost in get_ghosts()) * 0.1
            return ret

    def player_tick(self) -> Vector2:
        pos = get_myself().position
        vec = get_nearest_ghost().position - pos
        self.portkey_eval = None

        def convert_point(p):
            if connected_to(p):
                return p
            else:
                return find_possible_portkeys_to(p)[0].position

        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
        for i in get_items():
            if i.type == ItemType.GOLDEN_SNITCH:
                has_golden_snitch = True
                golden_snitch_pos = i.position

        """
        items = get_items()
        best_item = min(items, key=lambda x: self.evaluate_items(x), default=None)
        if get_myself().effect == EffectType.SORTINGHAT:
            return convert_point(pos + vec)
        if has_golden_snitch and get_myself().effect == EffectType.CLOAK:
            return golden_snitch_pos
        
        if best_item is not None and (distance(best_item.position, pos) < max(vec.length()*0.8,150) or vec.length() > 450):
            return convert_point(best_item.position)
        else:
            if vec.length() < 150 and get_myself().effect == EffectType.CLOAK:
                return pos - vec
            if vec.length() < 250 and not get_myself().dead:
                ret = min(self.get_close_positions(), key=lambda x: self.evaluate_position(x), 
                        default=None)
            else:
                ret = min(self.candidates, key=lambda x: self.evaluate_position(x),default=None)
            return convert_point(ret)
        """
        ret = min(self.candidates, key=lambda x: self.evaluate_position(x),default=None)
        return convert_point(ret)
