from pygame import Vector2

from api.api import *
import random
import math

class TeamAI(AI):

    def __init__(self):
        """
        self.candidates = []
        while len(self.candidates) < 75:
            i = Vector2(random.uniform(0, 1200), random.uniform(0, 800))
            if get_ground_type(i) != GroundType.OBSTACLE:
                self.candidates.append(i)
        """
        self.portkey_eval = None
        self.previous_target = None
        self.me = get_myself()
        self.ghosts = []
    
    def get_close_positions(self, radius):
        ret = [self.me.position + Vector2(random.uniform(-radius, radius), random.uniform(-radius, radius)) for i in range(50)]
        if self.previous_target is not None:
            ret.append(self.previous_target)
        return ret
    def evaluate_position(self, pos, far):
        #tries to find the most "empty" position that is nearby
        if get_ground_type(pos) == GroundType.OBSTACLE:
            return 10000
        portkey = False
        if not connected_to(pos):
            if self.portkey_eval is not None:
                return self.portkey_eval
            portkey = True
            pos = find_possible_portkeys_to(pos)[0].target
        ret = 0
        same_side = False
        for ghost in self.ghosts:
            ghostpos = ghost.position
            if connected(pos, ghostpos):
                same_side = True
            if ghost.chanting: 
                ghostpos = ghost.teleport_destination
            dis = distance(ghostpos, pos)
            ret -= min(500, dis) + min(200, dis)
        if same_side is False:
            ret -= 10000
        if portkey:
            self.portkey_eval = ret
        if ret > -5000 and get_time() < 120 * 60 and far:
            ret -= sum(distance(pos, player.position) for player in get_players()) / 4
        return ret
    
    def evaluate_items(self, item):
        #evaluates the value of an item
        ret = 0
        if item.type == ItemType.GOLDEN_SNITCH:
            if self.me.effect == EffectType.CLOAK: 
                return -10000
            else:
                return 10000
        elif item.type == ItemType.CLOAK:
            #no golden snitch strat
            has_golden_snitch = False
            for i in get_items():
                if i.type == ItemType.GOLDEN_SNITCH:
                    has_golden_snitch = True
            dis = distance(item.position, self.me.position)
            if has_golden_snitch: 
                if dis < 500:
                    return dis * 0.1
                else:
                    return dis * 0.3
            else:
                ret = distance(item.position, self.me.position) * 0.6
                #ret += min(distance(ghost.position, item.position) for ghost in get_ghosts()) * 0.2
                return ret
        elif item.type == ItemType.PATRONUS:
            return 0.6 * distance(item.position, self.me.position) + 0.5 * distance_to(get_nearest_ghost().position)
        elif item.type == ItemType.PETRIFICATION:
            multi = 1.2
            for i in get_players(): 
                if i != self.me and i.effect != EffectType.NONE:
                    multi -= 0.2
            return distance(item.position, self.me.position) * multi
        else:
            #Sorting hat
            ret = distance(item.position, self.me.position) * 0.25
            return ret

    def reachable(self, pos):
        #guesses if pos is reachable without gettting tagged
        dis = distance_to(pos)
        extra = distance(pos, get_nearest_ghost().position)
        if self.me.dead:
            return self.me.respawn_after * self.me.speed + extra > dis
        if self.me.effect == EffectType.REMOVED_SORTINGHAT:
            return self.me.effect_remain * self.me.speed + extra > dis
        return dis * get_nearest_ghost().speed < extra * self.me.speed
        
    def player_tick(self) -> Vector2:
        self.me = get_myself()
        pos = self.me.position
        vec = get_nearest_ghost().position - pos
        self.portkey_eval = None
        self.ghosts = get_ghosts()
        portkey = get_reachable_portkeys()

        def convert_point(p):

            if get_ground_type(p) == GroundType.OBSTACLE or connected_to(p):
                self.previous_target = p
                return p
            else:
                self.previous_target = find_possible_portkeys_to(p)[0].position
                return portkey[0].position

        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
        for i in get_items():
            if i.type == ItemType.GOLDEN_SNITCH:
                has_golden_snitch = True
                golden_snitch_pos = i.position

        items = get_items()
        best_item = min(items, key=lambda x: self.evaluate_items(x), default=None)
        if self.me.effect == EffectType.SORTINGHAT:
            return convert_point(pos + vec)
        if has_golden_snitch and self.me.effect == EffectType.CLOAK:
            if vec.length() < 150:
                return pos - vec
            return golden_snitch_pos
        
        if len(portkey) > 0:
            self.portkey_eval = self.evaluate_position(portkey[0].target, 1)

        if best_item is not None and (self.reachable(best_item.position)):
            return convert_point(best_item.position)
        else:
            if get_time() % 10 != 0 and self.previous_target != None:
                return convert_point(self.previous_target)
            else:
                self.previous_target = None
            if self.portkey_eval != None and self.portkey_eval <= -9000:
                return convert_point(portkey[0].position)
            if vec.length() < 150 and get_myself().effect == EffectType.CLOAK:
                return pos - vec
            if vec.length() > 450 or self.me.respawn_after > 120 or self.me.effect == EffectType.REMOVED_SORTINGHAT:
                ret = min(self.get_close_positions(600), key=lambda x: self.evaluate_position(x,1),default=None)

                if self.previous_target != None and self.evaluate_position(self.previous_target,1) - 50 < self.evaluate_position(ret,1):
                    ret = self.previous_target
                return convert_point(ret)
            if self.previous_target != None and distance_to(self.previous_target) > 350:
                self.previous_target = None
            ret = min(self.get_close_positions(max(150, vec.length()+100)), key=lambda x: self.evaluate_position(x,0),default=None)
            if ret == None:
                return pos - vec
            return convert_point(ret)
