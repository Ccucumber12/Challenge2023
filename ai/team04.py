'''
要再加上道具種類這個因素
tick時間轉換
考慮不同地圖中的地形(孤島 死角等)
'''
from api.api import *
from numpy import dot
class TeamAI(AI):
    def run_from_ghost(self):
        item_list = get_items()
        item_golden = []
        run = 0
        for item in item_list:
            if item.type == ItemType.GOLDEN_SNITCH :
                run = 1
                item_golden = item
                break
        all_ghosts = get_ghosts()
        close_ghosts = []
        myself = get_myself()
        for ghost in all_ghosts:
            if(distance(myself.position, ghost.position)<250):
                close_ghosts.append(ghost)
        all_items = get_items()
        # use vector to find the best way to run
        safe_items=[]
        if(len(all_items)!=0):
            for item in all_items:
                safe=1
                for ghost in close_ghosts:
                    vector_ghost_myself = myself.position-ghost.position
                    vector_item_myself = myself.position-item.position
                    dot_product=dot(vector_ghost_myself,vector_item_myself)
                    # print(dot_product)
                    if(dot_product<=0):
                        safe*=1
                    else:
                        safe*=0
                if(safe==1):
                    safe_items.append(item)
        if run:
            if myself.effect == EffectType.CLOAK:
                return item_golden.position
            for item in safe_items:
                if item.type == ItemType.CLOAK:
                    return item.position
        if(len(safe_items)!=0):
            best_types=[ItemType.SORTINGHAT,ItemType.PATRONUS]
            second_types=[ItemType.CLOAK,ItemType.PETRIFICATION]
            for item in safe_items:
                if(item.type in best_types):
                    # print("line40")
                    return item.position
            for item in safe_items:
                if(item.type in second_types):
                    # print("line45")
                    return item.position
        else:
            #len(safe_items)==0
            if(len(close_ghosts)<=2):
                sum=Vector2(0, 0)
                for ghost in close_ghosts:
                    vector_ghost_myself = myself.position-ghost.position
                    if vector_ghost_myself.length() > 0:
                        # Fix
                        standard_vector = vector_ghost_myself/vector_ghost_myself.magnitude()
                        sum+=standard_vector
                # print("line56")
                return sum*100 + myself.position
        # print("owo")
        # teleport_destination
        for ghost in close_ghosts:
            if(ghost.teleport_destination == myself):
                item_destination = all_items[0]
                return item_destination.position
        return myself.position
    def ArriveTime(self, pos):
        return 180000
    # run to ghost      
    def run_to_ghost(self):
        myPosition = get_myself().position
        ghostPosition = get_ghosts()[0].position
        ghostSpeed = get_ghosts()[0].speed * 60
        if get_myself().effect == EffectType.SORTINGHAT and get_myself().effect_remain / 60 > self.ArriveTime(get_nearest_ghost().position):
            return get_nearest_ghost().position   
    def azkaban(self) -> Vector2:
        all_ghosts = get_ghosts()
        close_ghosts = []
        myself = get_myself()
        all_items = get_items(SortKey.DISTANCE)
        item_golden = []
        run = 0
        for item in all_items:
            if item.type == ItemType.GOLDEN_SNITCH :
                run = 1
                item_golden = item
                break
        myposition = get_myself().position
        nearest_ghost = get_nearest_ghost().position
        left_ghost_cnt = 0
        right_ghost_cnt = 0
        for ghost in all_ghosts:
            if ghost.position.x < 600:
                left_ghost_cnt += 1
            else:
                right_ghost_cnt += 1
        if ((myself.position.x < 600) != (left_ghost_cnt < right_ghost_cnt)):        
            portkeys = get_reachable_portkeys()
            for portkey in portkeys:
                safe = 1
                for ghost in close_ghosts:
                    vector_ghost_myself = myself.position-ghost.position
                    vector_key_myself = myself.position-portkey.position
                    dot_product=dot(vector_ghost_myself, vector_key_myself)
                    if(dot_product<=0):
                        safe*=1
                    else:
                        safe*=0
                if(safe==1):
                    return portkey.position

        for ghost in all_ghosts:
            if(distance(myself.position, ghost.position)<250):
                close_ghosts.append(ghost)
        safe_items=[]
        if(len(all_items)!=0):
            for item in all_items:
                safe=1
                for ghost in close_ghosts:
                    vector_ghost_myself = myself.position-ghost.position
                    vector_item_myself = myself.position-item.position
                    dot_product=dot(ghost.position - myself.position, item.position - myself.position)
                    # print(vector_ghost_myself, vector_item_myself)
                    # print(dot_product)
                    if(dot_product<=0):
                        safe*=1
                    else:
                        safe*=0
                if(safe==1):
                    safe_items.append(item)
        if run:
            if myself.effect == EffectType.CLOAK:
                return item_golden.position
            for item in safe_items:
                if item.type == ItemType.CLOAK:
                    return item.position
        # print(safe_items)
        if(len(safe_items)!=0):
            best_types=[ItemType.SORTINGHAT,ItemType.PATRONUS]
            second_types=[ItemType.CLOAK,ItemType.PETRIFICATION]
            for item in safe_items:
                if(connected_to(item.position)):
                    return item.position
                # else:
                #     # 港口鑰
                #     nearest_portkeys = get_reachable_portkeys()
                #     if(nearest_portkeys):
                #         return nearest_portkeys[0].position - (nearest_ghost.position - myposition).normalize() * 100000
        else:
            #len(safe_items)==0
            if(len(close_ghosts)<=2):
                sum=Vector2(0, 0)
                for ghost in close_ghosts:
                    vector_ghost_myself = myself.position-ghost.position
                    standard_vector = vector_ghost_myself/vector_ghost_myself.magnitude()
                    sum+=standard_vector
                # print("line109")
                return sum*100 + myself.position
            # 檢查周圍是否有Ghost
        for ghost in close_ghosts:
            if(ghost.teleport_destination == myself):
                item_destination = all_items[0]
                return item_destination.position
        return myself.position
      
    def player_tick(self) -> Vector2:
        map_name=get_map_name()
        if(map_name == "snow"):
            return self.run_from_ghost()
        if(get_myself().effect == EffectType.SORTINGHAT):
            return self.run_to_ghost()
        if(map_name == "azkaban"):
            return self.azkaban()
        if(map_name == "snow"):
            return 
        #金探子
