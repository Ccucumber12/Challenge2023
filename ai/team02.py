from api.api import *

class TeamAI(AI):
    def distance_to_ghost(self,position):
          player=get_myself()
          myposition = get_myself().position
          ghostposition = get_nearest_ghost().position
          dis=distance(myposition,ghostposition)
          return dis
    def distance_to_item(self,position):
          player=get_myself()
          myposition = get_myself().position
          itemposition = get_nearest_item().position
          dis=distance(myposition,itemposition)
          return dis
      
    def item(self,Type):
         l=get_items(SortKey.DISTANCE)
         for i in l :
            if i.type == Type:
                    target=i.position
                    return target
    def isItin(self,l,Type):
        for i in l:
            if i.type == Type:
                return True
        return False

    def player_tick(self) -> Vector2:
        first = 0
        CLOAK = ItemType.CLOAK
        SORTINGHAT = ItemType.SORTINGHAT
        map=get_map_name()
        player=get_myself()
        l=get_items(SortKey.DISTANCE)
        target = get_myself().position
        # Fix

        if player.effect == EffectType.SORTINGHAT and self.distance_to_ghost(player.position)<1000:
            target = get_nearest_ghost().position
        elif player.effect == EffectType.CLOAK and \
              ItemType.GOLDEN_SNITCH in l :
             for i in l :
                if i == ItemType.GOLDEN_SNITCH:
                    target=l[i].position
                    break
        elif self.distance_to_ghost(player.position)<150 :
            vector = get_nearest_ghost().position - get_myself().position
            target = get_myself().position - vector
        elif first==0 and distance(get_nearest_ghost().teleport_destination,get_myself().position) <=140:
            target=get_nearest_player().position
            first=first+1
        elif first!=0 and distance(get_nearest_ghost().teleport_destination,get_myself().position) <=140:
             vector1 =get_nearest_ghost().teleport_destination - get_myself().position
             target = get_myself().position - vector1
        elif (self.isItin(l,ItemType.CLOAK)== True) and distance(get_nearest_item().position,get_myself().position)>250 and (self.isItin(l,ItemType.GOLDEN_SNITCH)== True):
              target=self.item(CLOAK)
        elif get_nearest_item() is not None and distance(get_nearest_item().position,get_myself().position)>450 and (self.isItin(l,ItemType.SORTINGHAT)== True):
            # Fix
            target=self.item(SORTINGHAT)
        
        elif len(l)>=2 and l[0].type==ItemType.GOLDEN_SNITCH:
            # Fix
            return l[1].position
        elif get_nearest_item() is not None:
            # Fix
            target = get_nearest_item().position
        if connected_to(target)==False and map == 'azkaban':
            sortkeys = get_reachable_portkeys()
            target=sortkeys[0].position
            
        return target 
