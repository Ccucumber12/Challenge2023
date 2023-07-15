from pygame import Vector2
from api.api import *

class TeamAI(AI):

    def check_pos_accessible(self, target) -> bool:
        dx = [1, 0, -1, 0]
        dy = [0, 1, 0, -1]
        score = 0
        m = 0
        if get_map_name() == "park":
            m = 10
        elif get_map_name() == "snow":
            m = 10
        elif get_map_name() == "azkaban":
            m = 20
        for i in range(1, 201, 20):
            for j in range(4):
                x = target.x + dx[j] * i
                y = target.y + dy[j] * i
                if not (0 < x < 1200 and 0 < y < 600) and get_ground_type(Vector2(x, y)) == GroundType.OBSTACLE:
                    score += 1
        # print(score)
        if score > m: return False
        else: return True

    def rotate_to_point(self, my_position):
        x = my_position.x
        y = my_position.y
        if get_map_name() == "river":
            return Vector2(600, 400)
        if get_map_name() == "snow":
            if 0 <= x < 600 and 0 <= y < 400:
                return Vector2(300, 200)
            elif 600 <= x <= 1200 and 0 <= y < 400:
                return Vector2(900, 200)
            elif 0 <= x < 600 and 400 <= y <= 800:
                return Vector2(230, 430)
            else: return Vector2(900, 600)
        elif get_map_name() == "azkaban":
            if 0 <= x < 600:
                return Vector2(160, 350)
            else:
                return Vector2(1030, 320)

    def detect_ghost_teleport(self, my_position):
        ghosts = get_ghosts()
        nearest_ghost_port = None
        min_distance = 10000
        for ghost in ghosts:
            if ghost.chanting:
                if distance_to(ghost.teleport_destination) < min_distance:
                    min_distance = distance_to(ghost.teleport_destination)
                    nearest_ghost_port = ghost.teleport_destination
        if nearest_ghost_port != None or min_distance > 200:
            return my_position
        else: return nearest_ghost_port

    def search_for_cloak(self, my_position) -> Vector2: # 在金探子在附近時尋找斗篷
        items = get_items()
        if len(items) == 0:
            return my_position
        for item in items:
            if item.type == ItemType.CLOAK:
                return item.position
        return get_nearest_item().position
    
    def restrict_target(self, target):
        x = target.x
        y = target.y
        # if 

    def escape(self, my_position) -> Vector2:
        dist = get_nearest_ghost().position - get_myself().position
        teleportDist = get_nearest_ghost().teleport_destination - get_myself().position

        # if get_myself().dead:
        #     if get_items() != []:
        #         target = get_nearest_item().position
        #     else:
        #         target = get_myself().position - (get_nearest_ghost().position - get_myself().position)*100

        target = my_position

        if (distance_to(get_nearest_ghost().position) <= 250) and get_myself().effect != EffectType.SORTINGHAT: # 如果鬼在附近 or 鬼傳送到附近 往反方向走
            ghost_position = get_nearest_ghost().position
            direction = ghost_position - my_position
            target = my_position - direction * 1
            # if not self.check_pos_accessible(target):
            #     target = self.rotate_to_point(my_position)
            if get_items() != []:
                if get_nearest_item().type != ItemType.PETRIFICATION and distance_to(get_nearest_item().position) <= distance_to(get_nearest_ghost().position):
                    target = get_nearest_item().position

        elif self.detect_ghost_teleport(my_position) != my_position:
            direction = self.detect_ghost_teleport(my_position) - my_position
            target = my_position - direction * 1
            
        else: # 拿道具
            # if get_time() > get_ticks_per_second()*60:
            #     items = get_items()
            #     decided = False
            #     if get_myself().effect == EffectType.CLOAK:
            #         for item in items:
            #             if item.type == ItemType.GOLDEN_SNITCH:
            #                 target = item.position
            #                 decided = True
            #                 break
            #     for item in items:
            #         if item.type == ItemType.CLOAK:
            #             target = item.position
            #             decided = True
            #             break
            #     if not decided and len(items) != 0:
            #         target = get_nearest_item().position

            # else:
            if get_items() != []:
                item = get_nearest_item() # 最近距離的道具
                for i in get_items():
                    if i.type == ItemType.GOLDEN_SNITCH:
                        if get_items()[0].type == ItemType.GOLDEN_SNITCH and get_myself().effect != EffectType.CLOAK: 
                            target = self.search_for_cloak(my_position)
                        elif get_items()[0].type == ItemType.GOLDEN_SNITCH and get_myself().effect == EffectType.CLOAK:
                            target = get_items()[0].position
                target = item.position # 移動過去
            else:
                target = get_myself().position - (get_nearest_ghost().position - get_myself().position)*100

        if not connected_to(target):
            if find_possible_portkeys_to(target) != []:
                target = find_possible_portkeys_to(target)[0].position

        return target

    def player_tick(self) -> Vector2:
        my_position = get_myself().position # 自己的位置
        return self.escape(my_position)