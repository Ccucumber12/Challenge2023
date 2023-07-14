from pygame import Vector2

from api.api import *
import random
import math

class TeamAI(AI):

    def __init__(self):
        self.candidates = [(937,33), (882,48), (923,91), (985,127), (974,171), (894,176), (866,134), (807,126), (797,76), (750,36), (628,40), (582,46), (613,106), (634,140), (680,155), (612,184), (571,208), (511,217), (453,222), (430,188), (389,158), (519,155), (345,109), (283,91), (243,91), (191,126), (268,159), (122,161), (94,182), (230,200), (254,244), (299,282), (346,313), (300,361), (241,347), (175,314), (140,286), (109,273), (114,379), (177,417), (245,423), (285,400), (220,505), (294,523), (231,575), (127,528), (357,389), (385,392), (422,387), (473,365), (492,326), (436,328), (395,356), (550,401), (586,415), (622,436), (612,487), (588,530), (519,541), (538,589), (542,625), (575,664), (659,683), (735,701), (798,725), (881,706), (713,641), (807,643), (744,602), (770,553), (811,580), (880,585), (926,557), (929,519), (888,461), (759,431), (859,409), (765,391), (718,359), (683,324), (773,290), (861,293), (905,328), (869,358), (946,333), (1012,338), (1076,337), (1129,382), (1152,418), (1060,438), (1081,490), (1135,518), (1158,548), (1155,631), (1080,660), (1041,710), (1047,216), (990,165), (1156,207), (1103, 278)]
        self.candidates = [Vector2(x) for x in self.candidates]
        for point in self.candidates:
            if get_ground_type(point) == GroundType.OBSTACLE:
                print("illegal", point)

        self.portkey_eval = None
        self.me = get_myself()
        self.ghosts = []
        self.directions = []
        # corners that should be avoided
        self.corners = [Vector2(422, 729), Vector2(24, 727), Vector2(26, 182), Vector2(1143, 114), Vector2(1193, 788)]

        
    def get_close_positions(self, radius, run):
        ret = [x for x in self.candidates if distance(x, self.me.position) < radius]
        if run:
            init_vec = Vector2(radius/3, 0)
            for i in range(36):
                ret.append(init_vec)
                init_vec.rotate(10)
        return ret
    def evaluate_position(self, pos, line):
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

        vec_length = (pos - self.me.position).length()
        for ghost in self.ghosts:
            ghostpos = ghost.position
            if ghost.chanting: 
                ghostpos = ghost.teleport_destination
            if connected(pos, ghostpos):
                same_side = True
                if line:
                    dis = (ghostpos - self.me.position).dot(pos - self.me.position) / max(1, vec_length) 
                    ret += min(350, dis)
                else:
                    dis = distance(ghostpos, pos)
                    ret -= min(1000, dis)
              
        if not line:
            ret -= sum(min(350, distance(pos, corner)) for corner in self.corners) * 2
        if same_side is False:
            ret -= 10000
        if portkey:
            self.portkey_eval = ret
        return ret

    def get_ghost_positions(self, ghost_positions):
        ghosts = get_ghosts(SortKey.DISTANCE)
        same_side = False
        for ghost in ghosts:
            ghostpos = ghost.position
            if ghost.chanting: 
                ghostpos = ghost.teleport_destination
            ghost_positions.append(ghostpos) 
            if connected_to(ghostpos):
                same_side = True
        return same_side

    def defense(self):
        vec = get_nearest_ghost().position - self.me.position
        ghosts = get_ghosts(SortKey.DISTANCE)
        ghost_positions = []
        same_side = self.get_ghost_positions(ghost_positions)
        
        def reachable(pos):
            #guesses if pos is reachable without getting tagged
            dis = distance_to(pos)
            extra = distance(pos, ghost_positions[0])
            if self.me.dead:
                return self.me.respawn_after * self.me.speed + extra > dis
            if self.me.effect == EffectType.REMOVED_SORTINGHAT:
                return self.me.effect_remain * self.me.speed + extra > dis
            return dis * ghosts[0].speed < extra * self.me.speed

        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
            
        items = [] 
        for item in get_items(SortKey.DISTANCE):
            if item.type == ItemType.GOLDEN_SNITCH:
                has_golden_snitch = True
                golden_snitch_pos = item.position
            if item.type != ItemType.GOLDEN_SNITCH and item.type != ItemType.PETRIFICATION:
                items.append(item)
                if reachable(item.position): 
                    return item.position
        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
        if has_golden_snitch and self.me.effect == EffectType.CLOAK:
            if vec.length() < 150:
                return self.me.position - vec
            return Vector2(600, 400)

        mindis = distance_to(ghost_positions[0])
        points = []
        if mindis > 350:
            points = self.get_close_positions(600, False)
            ret = min(points, key=lambda x: self.evaluate_position(x, 0),default=None)
            return ret
        else:
            points = self.get_close_positions(350, True)
            ret = min(points, key=lambda x: self.evaluate_position(x, 1),default=None)
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

    def offense(self):
        items = get_items()

        ghosts = get_ghosts(SortKey.DISTANCE)
        ghost_positions = []
        same_side = self.get_ghost_positions(ghost_positions)
        vec = ghost_positions[0] - self.me.position

        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
        for i in items:
            if i.type == ItemType.GOLDEN_SNITCH:
                has_golden_snitch = True
                golden_snitch_pos = i.position
        if has_golden_snitch and self.me.effect == EffectType.CLOAK:
            if vec.length() < 150:
                return self.me.position - vec
            return Vector2(600, 400)

        best_item = min(items, key=lambda x: self.evaluate_items(x), default=None)
        if len(items) > 0 and (distance_to(best_item.position) < max(vec.length()*0.8, 150) or vec.length() > 450 or self.me.dead or self.me.effect == EffectType.REMOVED_SORTINGHAT):
            return best_item.position 
        else:
            mindis = vec.length()
            points = []
            if mindis > 350:
                points = self.get_close_positions(600, False)
                ret = min(points, key=lambda x: self.evaluate_position(x, 0),default=None)
                return ret
            else:
                points = self.get_close_positions(350, True)
                ret = min(points, key=lambda x: self.evaluate_position(x, 1),default=None)
                return ret
            
    def player_tick(self) -> Vector2:
        self.me = get_myself()
        pos = self.me.position
        vec = get_nearest_ghost().position - pos
        self.portkey_eval = None
        self.ghosts = get_ghosts()
        portkey = get_reachable_portkeys()
        def convert_point(p):
            if get_ground_type(p) == GroundType.OBSTACLE or connected_to(p):
                return p
            else:
                return portkey[0].position
            
        if self.me.effect == EffectType.SORTINGHAT:
            return convert_point(self.me.position + vec)
        return convert_point(self.defense())
        """
        if get_time() < 120 * 60:
            return convert_point(self.defense())
        else:
            return convert_point(self.offense())
        """
         

       
