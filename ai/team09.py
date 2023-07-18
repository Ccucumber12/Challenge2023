from api.api import *


class TeamAI(AI):
    def __init__(self) -> None:
        self.far_dist = 400
        self.med_dist = 200
        self.close_dist = 100    
    def Escapetime(self):
        if (self.my_position.x < 70 or self.my_position.x > 1130) and (self.my_position.y < 70 or self.my_position.y > 730) :
            if abs(self.direction.y) > abs(self.direction.x) :
                return self.my_position + Vector2(self.direction.x * 10000, 0)
            else :
                return self.my_position + Vector2(0, self.direction.y * 10000)
        else:
            return self.my_position - self.direction * 10000
    def convert(self, position):
        global portkey,portkeys
        if get_ground_type(position) == GroundType.OBSTACLE or connected_to(position):
            return position
        portkeys = find_possible_portkeys_to(position)
        portkey = portkeys[0]
        
        #return portkey.position
        if connected_to(position) == True:
            return (position)
        else:
            return portkey.position

    def player_tick(self) -> Vector2:
        ghost_position = get_nearest_ghost().position # 最近的鬼位置
        self.my_position = get_myself().position # 自己的位置
        self.direction = ghost_position - self.my_position # 朝向鬼的方向
        getItem=get_items()
        Ghosts=get_ghosts()
        if get_map_name() == "azkaban":
            if get_nearest_item() != None:
                nearest_item_position = self.convert(get_nearest_item().position)
        #return nearest_item_position
            if get_myself().dead == True:
                if self.direction.length() <= self.med_dist:      #鬼很近
                    return self.Escapetime() # 往反方向走
                
                if get_nearest_item() != None:
                    return self.convert(nearest_item_position)
                return self.convert(get_nearest_player().position)
                #return self.my_position - direction * 10000
            else:
                if get_nearest_item() == None:
                    return self.convert(self.Escapetime())
                if get_nearest_item() != None:
                    nearest_item_position = self.convert(get_nearest_item().position)
                if self.direction.length() <=self.far_dist and get_myself().effect==EffectType.SORTINGHAT :     #有分類帽而且鬼很近
                    return ghost_position    #找鬼送死                                                            
                if self.direction.length() <=self.med_dist:      #鬼很近
                    self.portkeys = get_reachable_portkeys()
                    if self.portkeys !=None:
                        self.portkey=self.portkeys[0]
                        if self.my_position.distance_to(self.portkey.position) <=300:
                            return self.portkey.position
                        else:
                            return self.Escapetime()
                    #return self.my_position - self.direction*10000
                for i in range(len(getItem)):
                    while getItem[i].type==ItemType.GOLDEN_SNITCH in getItem == True  : #如果有金探子
                        if self.direction.length() <= self.close_dist :      #鬼很近(超級近)
                            return self.convert(self.Escapetime())
                            
                        if get_myself().effect==EffectType.CLOAK == True :  #已經有斗篷 
                            for i in range(len(getItem)):
                                if getItem[i].type==ItemType.GOLDEN_SNITCH:
                                    return self.convert(getItem[i].position)
                                    break
                        #return ItemType.GOLDEN_SNITCH.position
                        #if ItemType.CLOAK in getItem == True and ItemType.GOLDEN_SNITCH in getItem == False: #如果有金探子沒有斗篷
                        else:
                            for i in range(len(getItem)):
                                if getItem[i].type == ItemType.CLOAK:
                                    return self.convert(getItem[i].position)
                                    break
                    #return ItemType.CLOAK.position
                
                    else:
                        break
                for Ghost_teleportation in Ghosts:      #判斷鬼有沒有傳送
                    if Ghost_teleportation.chanting == True:
                        teleportation_direction = Ghost_teleportation.teleport_destination - self.my_position
                        if teleportation_direction.length() <=self.far_dist: #鬼傳送位置很近
                            return self.convert(self.my_position - Ghost_teleportation.teleport_destination) * 10000

                    
                else:
                    return self.convert(nearest_item_position) #找最近的道具
#還沒做阿茲卡班的部分
        else:
            if get_nearest_item() != None:
                nearest_item_position = get_nearest_item().position
        #return nearest_item_position
            if get_myself().dead == True:
                '''if self.direction.length() <= self.med_dist:      #鬼很近
                    return self.Escapetime() # 往反方向走'''
                
                if get_nearest_item() != None:
                    return nearest_item_position
                return get_nearest_player().position
                #return self.my_position - direction * 10000
            else:
                if get_nearest_item() == None:
                    return self.Escapetime()
                if get_nearest_item() != None:
                    nearest_item_position = get_nearest_item().position
                if self.direction.length() <=self.far_dist and get_myself().effect==EffectType.SORTINGHAT :     #有分類帽而且鬼很近
                    return ghost_position    #找鬼送死                                                            
                if self.direction.length() <=self.med_dist:      #鬼很近
                    return self.Escapetime() # 往反方向走
                for i in range(len(getItem)):
                    while getItem[i].type==ItemType.GOLDEN_SNITCH in getItem == True  : #如果有金探子
                        if self.direction.length() <= self.close_dist :      #鬼很近(超級近)
                            return self.Escapetime()
                            
                        if get_myself().effect==EffectType.CLOAK == True :  #已經有斗篷 
                            for i in range(len(getItem)):
                                if getItem[i].type==ItemType.GOLDEN_SNITCH:
                                    return getItem[i].position
                                    break
                        #return ItemType.GOLDEN_SNITCH.position
                        #if ItemType.CLOAK in getItem == True and ItemType.GOLDEN_SNITCH in getItem == False: #如果有金探子沒有斗篷
                        else:
                            for i in range(len(getItem)):
                                if getItem[i].type == ItemType.CLOAK:
                                    return getItem[i].position
                                    break
                    #return ItemType.CLOAK.position
                
                    else:
                        break
                for Ghost_teleportation in Ghosts:      #判斷鬼有沒有傳送
                    if Ghost_teleportation.chanting == True:
                        teleportation_direction = Ghost_teleportation.teleport_destination - self.my_position
                        if teleportation_direction.length() <=self.far_dist: #鬼傳送位置很近
                            return self.my_position - Ghost_teleportation.teleport_destination * 10000

                    
                else:
                    return nearest_item_position #找最近的道具