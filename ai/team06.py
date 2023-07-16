from pygame import Vector2
from api.api import *

class TeamAI(AI):
    mySpeed = get_myself().speed * get_ticks_per_second()
    def escape(self):
        vector = get_nearest_ghost().position - get_myself().position
        return get_myself().position - vector.normalize() * 10000 if vector.length() != 0 else get_myself().position
        # Fix

    def EscapeTime(self, myPosition, ghostPosition, ghostSpeed):
        return myPosition.distance_to(ghostPosition) / ghostSpeed

    def ArriveTime(self, Destination):
       return (Destination - get_myself().position).magnitude() / self.mySpeed
    def patronus(self):
        distance=myPosition.distance_to(ghostPosition)
        item = get_nearest_item()
        myPosition = get_myself().position
        ghostPosition = get_ghosts()[0].position
        distanceItemMyself=myPosition.distance_to(ItemType.PATRONUS.position)
        if distance>=60 and item.type==ItemType.PATRONUS and distanceItemMyself<=60:
            return myPosition
        elif distance<=60 and item.type==ItemType.PATRONUS and distanceItemMyself<=60:
            return item.position
    def beforetwomin (self):
        myPosition = get_myself().position
        ghostPosition = get_ghosts()[0].position
        ghostSpeed = get_ghosts()[0].speed * 60
        item = get_nearest_item()
        distanceItemMyself=myPosition.distance_to(item.position)
        distance=myPosition.distance_to(ghostPosition)
        mySpeed = get_myself().speed * get_ticks_per_second()
        time = get_time()
        items=get_items
        items = get_items(SortKey.DISTANCE)
        if time<= 7200:  
            for i in items :
                if i.type == ItemType.SORTINGHAT and myPosition.distance_to(i.position)<=200 :
                    item = i.position
                    return item#如果分類帽小於一定距離先去找分類帽
            if distance>=160 and item.type==ItemType.PATRONUS and distanceItemMyself<=60:
                return myPosition
            elif distance<=160 and item.type==ItemType.PATRONUS and distanceItemMyself<=60:
                return item.position
        if get_myself().effect == EffectType.SORTINGHAT and get_myself().effect_remain / 60 > self.ArriveTime(get_nearest_ghost().position):
            return get_nearest_ghost().position

        if item.type==ItemType.PATRONUS or item.type==ItemType.CLOAK and distanceItemMyself/mySpeed<self.EscapeTime(myPosition, ghostPosition, ghostSpeed):
            return item.position
        elif self.EscapeTime(myPosition, ghostPosition, ghostSpeed) < 3 and distanceItemMyself/mySpeed>self.EscapeTime(myPosition, ghostPosition, ghostSpeed):
            return self.escape()


        candidate_types = [ItemType.SORTINGHAT, ItemType.CLOAK, ItemType.PETRIFICATION]
        item = get_nearest_item()
        if item is not None:
            for i in get_items():
                if i.type == ItemType.GOLDEN_SNITCH:
                    return i.position

            if item.type in candidate_types:
                return item.position

        return myPosition
        #return myPosition
    def get_goldensnitch(self): 
        #item = get_GOLDEN_SNITCH.position
        items = get_items() # 包含場上存在的所有道具的 list
        for item in items:
            if item.type == ItemType.GOLDEN_SNITCH:
                
                return item
            else:
                return None
                
    
    def findCloak(self):
        """回傳場上最接近的隱形斗篷。如果不存在，則回傳 None。"""
        items = get_items(SortKey.DISTANCE)
        for item in items :
            if item.type == ItemType.CLOAK :
                return item
        return None
    
    #def distance_to_nearest_ghost(self):


    def ticks(self):
        golden_snitch = self.get_goldensnitch()
        if get_myself().effect is EffectType.CLOAK and golden_snitch is not None:
            return golden_snitch.position
        else:
            cloak = self.findCloak()
            if cloak is not None:
                return cloak.position
            else:
                return self.beforetwomin()


     


    #前兩分鐘逃鬼、拿道具


    

    #最後一分鐘，主要拿隱形斗篷

    def player_tick(self) -> Vector2:
       # map = get_map_name()
        #if map == "azkaban":
            
        myPosition = get_myself().position
        ghostPosition = get_ghosts()[0].position
        ghostSpeed = get_ghosts()[0].speed * 60
        item = get_nearest_item()
        distanceItemMyself=0 if item is None else myPosition.distance_to(item.position)
        # Fix
        distance=myPosition.distance_to(ghostPosition)
        mySpeed = get_myself().speed * get_ticks_per_second()
        time = get_time()
        items=get_items
        items = get_items(SortKey.DISTANCE)
        items_type = [i.type for i in items]
        if time >= 7200 and ItemType.GOLDEN_SNITCH in items_type : #確認時間過了兩分鐘
                #myPosition = get_myself().position
                #CLOAKPosition = get_nearest_item(ItemType.CLOAK)

            
            return self.ticks()
        
        
        if time<= 7200 or ItemType.GOLDEN_SNITCH not in items_type:  
            for i in items :
                if i.type == ItemType.SORTINGHAT and myPosition.distance_to(i.position)<=200 :
                    item = i.position
                    return item#如果分類帽小於一定距離先去找分類帽
            if item is None or (distance>=160 and item.type==ItemType.PATRONUS and distanceItemMyself<=60):
                # Fix
                return myPosition
            elif distance<=160 and item.type==ItemType.PATRONUS and distanceItemMyself<=60:
                return item.position
        if get_myself().effect == EffectType.SORTINGHAT and get_myself().effect_remain / 60 > self.ArriveTime(get_nearest_ghost().position):
            return get_nearest_ghost().position

        if item.type==ItemType.PATRONUS or item.type==ItemType.CLOAK and distanceItemMyself/mySpeed<self.EscapeTime(myPosition, ghostPosition, ghostSpeed):
            return item.position
        elif self.EscapeTime(myPosition, ghostPosition, ghostSpeed) < 3 and distanceItemMyself/mySpeed>self.EscapeTime(myPosition, ghostPosition, ghostSpeed):
            return self.escape()


        candidate_types = [ItemType.SORTINGHAT, ItemType.CLOAK, ItemType.PETRIFICATION]
        item = get_nearest_item()
        if item is not None:
            for i in get_items():
                if i.type == ItemType.GOLDEN_SNITCH:
                    return i.position

            if item.type in candidate_types:
                return item.position

        return myPosition
    

