from pygame import Vector2

from api.api import *
import random
import math

class TeamAI(AI):

    def __init__(self):
        self.candidates = [(937,33), (882,48), (923,91), (985,127), (974,171), (894,176), (866,134), (807,126), (797,76), (750,36), (628,40), (582,46), (613,106), (634,140), (680,155), (612,184), (571,208), (511,217), (453,222), (430,188), (389,158), (519,155), (345,109), (283,91), (243,91), (191,126), (268,159), (122,161), (94,182), (230,200), (254,244), (299,282), (346,313), (300,361), (241,347), (175,314), (140,286), (109,273), (114,379), (177,417), (245,423), (285,400), (220,505), (294,523), (231,575), (127,528), (357,389), (385,392), (422,387), (473,365), (492,326), (436,328), (395,356), (550,401), (586,415), (622,436), (612,487), (588,530), (519,541), (538,589), (542,625), (575,664), (659,683), (735,701), (798,725), (881,706), (713,641), (807,643), (744,602), (770,553), (811,580), (880,585), (926,557), (929,519), (888,461), (759,431), (859,409), (765,391), (718,359), (683,324), (773,290), (861,293), (905,328), (869,358), (946,333), (1012,338), (1076,337), (1129,382), (1119, 338), (1060,438), (1081,490), (1135,518), (1158,548), (1155,631), (1080,660), (1041,710), (1047,216), (990,165), (1156,207), (1103, 278), (805, 100), (673, 169), (164, 135), (52, 196)]
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
                    wei = distance_to(ghostpos)
                    if min(distance(ghostpos, pos), wei) < 600:
                        dis = (ghostpos - self.me.position).dot(pos - self.me.position) / max(1, vec_length) 
                        ret += min(350, dis / (max(1, wei) / 200))
                else:
                    dis = distance(ghostpos, pos)
                    ret -= min(1000, dis)
              
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
        ghosts = get_ghosts(SortKey.DISTANCE)
        players = get_players() 
        ghost_positions = []
        same_side = self.get_ghost_positions(ghost_positions)
        
        ghosts, ghost_positions = zip(*sorted(zip(ghosts, ghost_positions), key=lambda x: distance_to(x[1])))
        vec = ghost_positions[0] - self.me.position
        
        def reachable(pos):
            #guesses if pos is reachable without getting tagged
            dis = distance_to(pos)
            extra = distance(pos, ghost_positions[0])
            if ghosts[0].chanting and distance_to(ghost_positions[0]) < 40:
                return dis < ghosts[0].teleport_after * self.me.speed
            if self.me.dead:
                return self.me.respawn_after * self.me.speed + extra > dis
            if self.me.effect == EffectType.REMOVED_SORTINGHAT:
                return self.me.effect_remain * self.me.speed + extra > dis
            return dis * ghosts[0].speed < extra * self.me.speed

        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
            
        items = [] 

        has_golden_snitch = False
        golden_snitch_pos = (0, 0)
        for item in get_items(SortKey.DISTANCE):
            if item.type == ItemType.GOLDEN_SNITCH:
                has_golden_snitch = True
                golden_snitch_pos = item.position

        def impossible(item):
            #determines whether item is impossible to get to first
            min_reach_time = 1000
            respawn_time = 0
            for player in players:
                if player.id == self.me.id:
                    if player.dead:
                        respawn_time = player.respawn_after
                    continue
                reach_time = distance(player.position, item.position) / player.speed
                if player.dead:
                    reach_time = max(reach_time, player.respawn_after)
                min_reach_time = min(min_reach_time, reach_time)
            return min_reach_time <= respawn_time

        minutes = get_time() // 3600
        def stall(item):
            #determines whether to wait before getting item
            if distance_to(item.position) > 60:
                return False
            if vec.length() < 100+20*minutes or (item.type == ItemType.PATRONUS and vec.length() < 150+20*minutes):
                return False
            for player in players:
                if player.id == self.me.id:
                    continue
                reach_time = distance(player.position, item.position) / player.speed
                if player.dead:
                    reach_time = max(reach_time, player.respawn_after)
                if reach_time < 30:
                    return False
            if item.type == ItemType.CLOAK:
                if has_golden_snitch:
                    return False
                if vec.length() > 500 or self.me.effect == EffectType.REMOVED_SORTINGHAT:
                    return True
            if item.type != ItemType.PATRONUS and item.type != ItemType.SORTINGHAT:
                return False
            return True

        if has_golden_snitch and self.me.effect == EffectType.CLOAK:
            if vec.length() < 150:
                return self.me.position - vec
            return Vector2(600, 400)

        for item in get_items(SortKey.DISTANCE):
            if impossible(item):
                continue
            if item.type != ItemType.GOLDEN_SNITCH and item.type != ItemType.PETRIFICATION:
                items.append(item)
                if reachable(item.position): 
                    if stall(item):
                        return self.me.position
                    return item.position

        mindis = distance_to(ghost_positions[0])
        points = [item.position for item in items]
        if mindis > 350+20*minutes:
            points = self.get_close_positions(600, False)
            ret = min(points, key=lambda x: self.evaluate_position(x, 0),default=None)
            return ret
        else:
            points = self.get_close_positions(350+20*minutes, True)
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
         

       
