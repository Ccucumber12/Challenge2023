#鬼太近會逃跑（190）
#沒有隱形就追道具
#有隱形且和金探子距離（250）就追金探子
#沒道具就逃離鬼
from api.api import *
from pygame import Vector2


class TeamAI(AI):

    loc = [0,0]
    t = 0

    def player_tick(self):
        my_position = get_myself().position # 自己的位置
        my_effectType = get_myself().effect #自己身上	的效果
        map_items = get_items() #所有道具資料
        k = False #是否有金探子
        ghost_position = get_nearest_ghost().position # 最近的鬼位置
        my_position = get_myself().position # 自己的位置
        direction = ghost_position - my_position # 朝向鬼的方向
        item = get_nearest_item()
        #item_position = get_nearest_item().position

        nearest_GS_position = Vector2()
        nearest_non_GS_position = Vector2()


###
        '''
        if my_position == self.loc: #count stucking time
            self.t += 1
            if self.t >= 20: #prevent stucking
                self.t = 0
                return item_position
            else:
                True
            
        else:
            self.loc = my_position
        '''
        #逃鬼
        if not (my_effectType == EffectType.SORTINGHAT or my_effectType == EffectType.REMOVED_SORTINGHAT or get_myself().dead):
            if distance_to(ghost_position) < 190 :
                # print("逃鬼1")
                return my_position - direction * 10000 # 往鬼反方向走
        t = False


        for i in map_items:
            map_itemType = i.type
            if map_itemType == ItemType.GOLDEN_SNITCH:
                if k:
                    if my_position.distance_to(nearest_GS_position) > my_position.distance_to(i.position):
                        nearest_GS_position = i.position
                else:
                    nearest_GS_position = i.position
                    #找出離自己最近的金探子位置
                    k = True
            else:
                if t:
                    if my_position.distance_to(nearest_non_GS_position) > my_position.distance_to(i.position) and \
                        (my_position.distance_to(i.position)**2 + my_position.distance_to(get_nearest_ghost().position)**2 < distance(get_nearest_ghost().position,i.position)**2 or\
                        my_position.distance_to(get_nearest_ghost().position) > my_position.distance_to(i.position)*2):
                        nearest_non_GS_position = i.position
                else:
                    nearest_non_GS_position = i.position
                    t = True

        
        if k and my_effectType == EffectType.CLOAK:
            if my_position.distance_to(nearest_GS_position) <= 250:
                #如果 自己和金探子的距離<=200
                # print("追金嘆子")
                return nearest_GS_position #追金探子



        if item is None:
            # print("桃鬼2")
            return my_position - direction * 10000 # 往鬼反方向走

        # print("追道具")
        return nearest_non_GS_position
