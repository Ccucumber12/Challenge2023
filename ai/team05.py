from api.api import *
import random


class TeamAI(AI):
    thresh_ghost = 0
    thresh_item = 0
    thresh_port = 0
    thresh_chant = 0
    def __init__(self) :
        if get_map_name() == "azkaban" :
            self.thresh_ghost = 180
            self.thresh_item = 150
            self.thresh_port = 150
            self.thresh_chant = 160
        elif get_map_name() == "snow" :
            self.thresh_ghost = 200
            self.thresh_item = 150
            self.thresh_port = 150
            self.thresh_chant = 180

    def run_away(self, ghost) :
        my_position = get_myself().position
        direction = ghost.position - my_position
        return my_position - direction * 10000
    def small_vector(self) :
        vec = Vector2(random.random() - random.random(), random.random() - random.random())
        return vec.normalize() * 60
    def go_near(self, position) :
        eps = get_myself().position - position
        if(distance_to(position) == 0) :
            return position
        else :
            to = position + eps.normalize() * 60
            if get_ground_type(to) == GroundType.OBSTACLE :
                return position
            else :
                return to
    def player_tick(self) -> Vector2:
        me = get_myself()
        my_position = me.position
        dis_to_ghost = distance(me.position, get_nearest_ghost().position)


        ghosts = get_ghosts()
        ghosts_near = list(filter(lambda x : connected_to(x.position), ghosts))
        ghosts_near.sort(key=lambda x:distance_to(x.position))
        ghosts_far = list(filter(lambda x : not connected_to(x.position), ghosts))
        port_keys = list(filter(lambda x : connected_to(x.position), get_portkeys()))
        port_keys.sort(key=lambda x: distance_to(x.position))
        items = list(filter(lambda x : connected_to(x.position), get_items()))
        items.sort(key=lambda x: distance_to(x.position))
        # calculate dis to chanting
        bad_ghosts = list(filter(lambda x : connected_to(x.teleport_destination), ghosts))
        bad_ghost = None
        dis_to_chanting = 10000000000000000000
        if len(bad_ghosts) != 0 :
            bad_ghost = min(bad_ghosts, key = lambda x : distance_to(x.teleport_destination))
            dis_to_chanting = distance_to(bad_ghost.teleport_destination)
        # sorting hat
        if me.effect == EffectType.CLOAK:
            for item in items:
                if item.type == ItemType.GOLDEN_SNITCH and distance_to(item.position) <= 100:
                    return item.position
        if me.dead:
            if me.respawn_after / get_ticks_per_second() >= 2: #死亡前三秒
                for item in items:
                    if item.type == ItemType.CLOAK or item.type == ItemType.PATRONUS \
                            or item.type == ItemType.SORTINGHAT:
                        if (distance_to(item.position) > 60):
                            return item.position
                        else:
                            return me.position
            else:
                if distance_to(get_nearest_item().position) <= 60:
                    return me.position
                else:
                    return 2 * me.position - get_nearest_ghost().position

        if me.effect == EffectType.SORTINGHAT and 1 <= len(ghosts_near) <= 2:
            return ghosts_near[0].position

        # deal with items
        goals = []
        for i in items :
            if i.type == ItemType.PETRIFICATION or i.type == ItemType.GOLDEN_SNITCH :
                continue
            elif len(goals) == 0:
                goals.append(i)
            elif abs(distance(me.position, i.position) - \
                    distance(me.position, goals[0].position)) <= 10:
                goals.append(i)

        goal = None
        if len(goals) != 0:
            goal = min(goals, key=lambda x : x.id)

        # states 
        state = (goal != None and distance(me.position, goal.position) <= self.thresh_item)
        state2 = (distance_to(get_nearest_player().position)) <= self.thresh_ghost
        state3 = len(ghosts_near) > len(ghosts_far)
        state4 = 0
        if len(port_keys) >= 1 :
            state4 = (distance_to(port_keys[0].position) <= self.thresh_port)
        if (state == 0 and (dis_to_ghost <= self.thresh_ghost or dis_to_chanting <= self.thresh_chant)):
            if state4 == 1 and state3 == 1 and len(port_keys) >= 1:
                return port_keys[0].position
            elif dis_to_ghost <= self.thresh_ghost :
                return self.run_away(get_nearest_ghost())
            else :
                direction = bad_ghost.teleport_destination - my_position
                if distance_to(bad_ghost.teleport_destination) == 0:
                    return my_position + self.small_vector()
                else :
                    return my_position - direction * 10000
        elif (state == 1 and (dis_to_ghost <= self.thresh_ghost or dis_to_chanting <= self.thresh_chant 
            or state2 == 1)):
            return goal.position
        else :
            if state3 == 1 and len(port_keys) >= 1:
                return port_keys[0].position
            elif goal != None:
                return self.go_near(goal.position)
            else :
                return my_position + self.small_vector()
