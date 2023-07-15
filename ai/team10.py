from api.api import *

class TeamAI(AI):

    def EscapeTime(self, myPosition, ghostPosition, ghostSpeed):
        return (myPosition - ghostPosition).magnitude() / ghostSpeed
    
    def available_portkey(self, position):
        #判斷走到 position 時是否需要經過港口鑰，並回傳目標位置
        if get_ground_type(position) == GroundType.OBSTACLE or connected_to(position): # 取得position的地面類型 == 地點為港口鑰 or 能不能不透過港口鑰到達position
            return position
        portkeys = find_possible_portkeys_to(position) # 要走到position可以用哪些港口鑰
        portkey = portkeys[0] # 它回傳的是list, 但在這張圖最多只會有一個可以用的港口鑰
        return portkey.position # 港口鑰
    
    def find_distance(self, item: Item) -> Item | Portkey:
        #找出想要到達 item 所在的位置，當前 tick 最短的距離
        best_dis1 = 10000000
        if connected_to(item.position):
            my_position = get_myself().position # 自己的位置
            best_dis1 = (item.position - my_position).magnitude()
        portkeys = find_possible_portkeys_to(item.position)
        best = None
        best_dis2 = 10000000
        for portkey in portkeys:
            begin = portkey.position #進入的港口鑰
            end = portkey.target #出去的港口鑰
            dis = distance_to(begin) + distance(end, item.position) 
            if best == None or dis < best_dis2 :
                best = portkey
                best_dis2 = dis
        return min(best_dis1, best_dis2)
    
    def player_tick_azkaban(self) -> Vector2:
        # escape_time
        ghost_position = get_nearest_ghost().position # 最近的鬼位置
        my_position = get_myself().position # 自己的位置
        ghostSpeed = get_ghosts()[0].speed * 60
        #print(self.EscapeTime(my_position, ghost_position, ghostSpeed))
        escape_time = (self.EscapeTime(my_position, ghost_position, ghostSpeed))

        if ghost_position != my_position:
            direction = (ghost_position - my_position).normalize() * 100 # 朝向鬼的方向
        else:
            direction = Vector2(300, 400)
        # 拿到分類帽後自殺
        myeffect = get_myself().effect
        if myeffect == EffectType.SORTINGHAT:
            return self.available_portkey(ghost_position)
        # 找到我要的道具
        all_item = get_items() # 所有道具
        all_item.sort(key=self.find_distance)
        for item in all_item:
            # 移動順序
            if not connected_to(item.position):
                continue
            if (item.type is ItemType.SORTINGHAT or item.type is ItemType.CLOAK) and escape_time > 1.5: #追分類帽&隱形斗篷, error
                return item.position
            elif escape_time > 1.5 : #追其他道具, 且不追離鬼太近的, error
                return item.position

        portkey_pos = get_reachable_portkeys()[0].position
        if escape_time < 2 and distance_to(portkey_pos) > 200: #避鬼
            for i in range(36):  
                if get_ground_type(my_position - direction) != GroundType.OBSTACLE:
                    return my_position - direction
                direction.rotate(10)
            return my_position - direction # 往反方向走
        else: #如果沒事就往港口鑰走
            return portkey_pos
            #return (self.available_portkey(my_position))

    def get_ghost_dirs(self):
        ghost_list = get_ghosts()
        myself = get_myself()
        ghost_dirs = []
        for ghost in ghost_list:
            vec = (ghost.position - myself.position)
            if vec.length() < 200:
                ghost_dirs.append(vec)
        return ghost_dirs
    
    def get_available_items(self, ghost_dirs):
        item_list = get_items()
        myself = get_myself()
        answer = []
        for item in item_list:
            ok = True
            item_dir = item.position - myself.position
            for ghost_dir in ghost_dirs:
                if item_dir * ghost_dir >= 0:
                    ok = False
            if ok:
                answer.append(item)
        return answer

    def get_most_wanted_item(self, item_list):
        # TODO: if empty then run away from ghosts
        # ( i am too lazy to implement that , so i will leave it for you guys) 
        myself = get_myself()
        if len(item_list) == 0:
            return myself.position
        nearest_item = item_list[0]
        nearest_item_dist = (item_list[0].position - myself.position).length()
        for item in item_list:
            dist = (item.position - myself.position).length()
            if dist < nearest_item_dist:
                nearest_item = item
                nearest_item_dist = dist
        return nearest_item.position

    def go_to_get_items_or_not(self, player_list, item_list, item):
        dist_list = []
        for i in player_list:
            dist_list.append(i.position.distance_to(item.position))
        return dist_list
                    
                      

##############ghost_dirs = self.get_ghost_dirs()item_list = self.get_available_items(ghost_dirs)destination = self.get_most_wanted_item(item_list)return destination######################################################


    def player_tick_snow(self,a = 0):
        my_effect = get_myself().effect
        my_position = get_myself().position
        ghost_position = get_nearest_ghost().position
        item_list = get_items()
        player_list = get_players()
        if my_effect == EffectType.REMOVED_SORTINGHAT:
            self.a = 420
        self.a = a-1
        if get_myself().dead and (get_myself().respawn_after == 60) or (my_effect == EffectType.REMOVED_SORTINGHAT and a >= 0):
            for item in item_list:
                return  item.position
        has_golden_snitch = False
        golden_snitch_pos = ()
        for item in item_list:
            if item.type == ItemType.GOLDEN_SNITCH:
                has_golden_snitch = True
                golden_snitch_pos = item.position

        if my_effect == EffectType.SORTINGHAT:
            return ghost_position

        if my_effect == EffectType.CLOAK and has_golden_snitch and distance_to(golden_snitch_pos) < 300:
            return golden_snitch_pos

        distance_limit = [0, 150, 200, 225]
        if (distance_to(ghost_position) < distance_limit[len(get_ghosts())]):
            direction = ghost_position - my_position
            for item in item_list:
                if item.type == ItemType.SORTINGHAT or item.type ==ItemType.CLOAK or item.type ==ItemType.PATRONUS:
                    if ghost_position.distance_to(item.position) / get_nearest_ghost().speed > distance_to(item.position)/get_myself().speed:
                        return item.position
                    else:
                        return my_position - direction*10000
                else:
                    return my_position - direction*10000

        if  len(item_list) == 0:
            myself = get_myself()
            target_player = get_myself()
            target_player_dist = (ghost_position - myself.position).length()
            for i in player_list:
                dist = (ghost_position - i.position).length()
                if dist > target_player_dist:
                    target_player = i
                    target_player_dist = dist
            return target_player.position
        
        for item in item_list:
            distance_list = self.go_to_get_items_or_not(player_list, item_list, item)
            for i in range(0,4):
                if distance_to(item.position)<=distance_list[i]:
                    return  item.position
        for item in item_list:
            if item.type == ItemType.SORTINGHAT:
                return item.position
        return get_nearest_item().position
    
    def player_tick(self):
        if get_map_name() == 'azkaban':
            return self.player_tick_azkaban()
        else:
            return self.player_tick_snow()
