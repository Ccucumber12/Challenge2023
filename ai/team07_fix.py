from pygame import Vector2
from api.api import *

class TeamAI(AI):
    mySpeed = get_myself().speed * get_ticks_per_second()
    def escape(self):
        vector = get_nearest_ghost().position - get_myself().position
        # FIX
        if vector.length() == 0:
            return get_myself().position
        else:
            return get_myself().position - vector.normalize() * 100000

    def EscapeTime(self, myPosition, ghostPosition, ghostSpeed):
        return myPosition.distance_to(ghostPosition) / ghostSpeed
    
    def ArriveTime(self, Destination):
       return (Destination - get_myself().position).magnitude() / self.mySpeed

    def player_tick(self) -> Vector2:
        myPosition = get_myself().position
        ghostPosition = get_ghosts()[0].position
        ghostSpeed = get_ghosts()[0].speed * 60
        candidate_types1m = [ItemType.SORTINGHAT, ItemType.CLOAK, ItemType.PATRONUS,ItemType.PETRIFICATION]
        candidate_types=[ItemType.SORTINGHAT, ItemType.CLOAK, ItemType.PATRONUS]
        item = get_nearest_item()
        if get_time() <=3600:
            
            if get_myself().effect == EffectType.SORTINGHAT and get_myself().effect_remain / 60 > self.ArriveTime(get_nearest_ghost().position):
                return get_nearest_ghost().position
            if self.EscapeTime(myPosition, ghostPosition, ghostSpeed) < 2 + get_time()/10800 :
                if get_nearest_item() is not None and (get_nearest_item().type == ItemType.SORTINGHAT or get_nearest_item().type == ItemType.PATRONUS):
                    # FIX
                    # print(1)
                    return get_nearest_item().position
                else:
                    return self.escape()
        
        
            if item is not None:
                for i in get_items():
                    if i.type == ItemType.GOLDEN_SNITCH:
                        return i.position        
                    if get_time()<=3600:
                        if item.type in candidate_types1m:
                            return item.position
                    else:
                        if item.type in candidate_types:
                            return item.position
                        elif ItemType == ItemType.PETRIFICATION:
                            return item.position
            
            return myPosition
        elif get_time()<=7200:
            if get_myself().effect == EffectType.SORTINGHAT and get_myself().effect_remain / 60 > self.ArriveTime(get_nearest_ghost().position):
                return get_nearest_ghost().position
            if self.EscapeTime(myPosition, ghostPosition, ghostSpeed) < 2 + get_time()/10800 :
                if get_nearest_item() is not None and (get_nearest_item().type == ItemType.SORTINGHAT or get_nearest_item().type == ItemType.PATRONUS):
                    # FIX
                    # print(1)
                    return get_nearest_item().position
                else:
                    return self.escape()
        
        
            if item is not None:
                for i in get_items():
                    if i.type == ItemType.GOLDEN_SNITCH:
                        return i.position        
                    if get_time()<=3600:
                        if item.type in candidate_types1m:
                            return item.position
                    else:
                        if item.type in candidate_types:
                            return item.position
                        elif ItemType == ItemType.PETRIFICATION:
                            return item.position
            
            return myPosition
        else:
            if get_myself().effect == EffectType.SORTINGHAT and get_myself().effect_remain / 60 > self.ArriveTime(get_nearest_ghost().position):
                return get_nearest_ghost().position
            if self.EscapeTime(myPosition, ghostPosition, ghostSpeed) < 2 + get_time()/10800 :
                if get_nearest_item() is not None and (get_nearest_item().type == ItemType.SORTINGHAT or get_nearest_item().type == ItemType.PATRONUS):
                    # FIX
                    # print(1)
                    return get_nearest_item().position
                else:
                    return self.escape()
        
        
            if item is not None:
                for i in get_items():
                    if i.type == ItemType.GOLDEN_SNITCH:
                        return i.position        
                    if get_time()<=3600:
                        if item.type in candidate_types1m:
                            return item.position
                    else:
                        if item.type in candidate_types:
                            return item.position
                        elif ItemType == ItemType.PETRIFICATION:
                            return item.position
            
            return myPosition
