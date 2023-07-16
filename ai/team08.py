from api.api import *
from pygame import Vector2

class TeamAI(AI):
	def convert(self, originTarget) ->Vector2:  #港口鑰
		if connected_to(originTarget):
			return originTarget
		else: 
			allPortkey = find_possible_portkeys_to(originTarget, SortKey.DISTANCE)
			allGhost = get_ghosts() 
			if len(allPortkey) == 0:
				return originTarget
			score = []
			for i in range(len(allPortkey)): 
				min_dis = distance(allPortkey[i].position, allGhost[0].position) 
				for j in range(1, len(allGhost)):
					dist = distance(allPortkey[i].position, allGhost[j].position) 
					if min_dis > dist:
						min_dis = dist 
				for j in range(len(allGhost)):
					dist = distance(allPortkey[i].target, allGhost[j].position) 
					if min_dis > dist:
						min_dis = dist 
				score.append(min_dis)
			newTarget = allPortkey[score.index(max(score))].position
			return newTarget
	def slow_convert(self, originalTarget):
		if get_ground_type(originalTarget) == GroundType.SLOW:
			return originalTarget
		myPosition = get_myself().position
		vector = originalTarget - myPosition
		if vector.magnitude()==0 :
			return originalTarget
		for i in range(0,60,3):
			if get_ground_type(vector.rotate(i) + myPosition) != GroundType.SLOW:
				return vector.rotate(i) + myPosition
			if get_ground_type(vector.rotate(-i) + myPosition) != GroundType.SLOW:
				return vector.rotate(-i) + myPosition
		return originalTarget
		
	def escape(self, ghostPosition) -> Vector2:  # 逃跑
		vector = ghostPosition - get_myself().position #最近的鬼的方向
		vector = -vector
		vector = 50 * vector.normalize()
		for i in range(0,120,10):
			ground_type_1 = get_ground_type(get_myself().position + vector.rotate(i))
			ground_type_2 = get_ground_type(get_myself().position + vector.rotate(i)*2)
			ground_type_3 = get_ground_type(get_myself().position + vector.rotate(-i))
			ground_type_4 = get_ground_type(get_myself().position + vector.rotate(-i)*2)
			if ground_type_1 != GroundType.OBSTACLE and ground_type_2 != GroundType.OBSTACLE \
					and ground_type_1 != GroundType.SLOW and ground_type_2 != GroundType.SLOW:
				return get_myself().position + vector.rotate(i)
			if ground_type_3 != GroundType.OBSTACLE and ground_type_4 != GroundType.OBSTACLE \
					and ground_type_3 != GroundType.SLOW and ground_type_4 != GroundType.SLOW:
				return get_myself().position + vector.rotate(-i)
		for i in range(0,120,10):
			ground_type_1 = get_ground_type(get_myself().position + vector.rotate(i))
			ground_type_3 = get_ground_type(get_myself().position + vector.rotate(-i))
			if ground_type_1 != GroundType.OBSTACLE and ground_type_1 != GroundType.SLOW:
				return get_myself().position + vector.rotate(i)
			if ground_type_3 != GroundType.OBSTACLE and ground_type_3 != GroundType.SLOW:
				return get_myself().position + vector.rotate(-i)
		for i in range(0,120,10):
			ground_type_1 = get_ground_type(get_myself().position + vector.rotate(i))
			ground_type_2 = get_ground_type(get_myself().position + vector.rotate(i)*2)
			ground_type_3 = get_ground_type(get_myself().position + vector.rotate(-i))
			ground_type_4 = get_ground_type(get_myself().position + vector.rotate(-i)*2)
			if ground_type_1 != GroundType.OBSTACLE and ground_type_2 != GroundType.OBSTACLE:
				return get_myself().position + vector.rotate(i)
			if ground_type_3 != GroundType.OBSTACLE and ground_type_4 != GroundType.OBSTACLE:
				return get_myself().position + vector.rotate(-i)
		for i in range(0,120,10):
			ground_type_1 = get_ground_type(get_myself().position + vector.rotate(i))
			ground_type_3 = get_ground_type(get_myself().position + vector.rotate(-i))
			if ground_type_1 != GroundType.OBSTACLE:
				return get_myself().position + vector.rotate(i)
			if ground_type_3 != GroundType.OBSTACLE:
				return get_myself().position + vector.rotate(-i)
		return get_myself().position + vector

	def itemg(self) -> Vector2:  # 拿道具
		#有金探子與斗篷，去追斗篷----------------------
		isgold = False #是否有金探子在場
		iscloak = False #是否有隱形斗篷在場
		for i in get_items():
			if i.type == ItemType.GOLDEN_SNITCH:
				isgold=True
			elif i.type == ItemType.CLOAK:
				iscloak=True
			#print(i.type,":",round(self.itemtime(myPosition, i.position, myspeed),3),end=" ")
		if iscloak and isgold:
			find=3000
			for i in get_items():
				if i.type == ItemType.CLOAK:
					if distance(get_myself().position, i.position)<find:
						re=i.position
						find=distance(get_myself().position, i.position)
			return re
		#----------------------------------------------------
		item = self.nearest_reachable() # 最近距離的道具
		return item.position # 移動過去

	def nearest_reachable(self): #有玩家離最近道具更近
		allPlayers = get_players() #裝所有人
		allItems = get_items(SortKey.DISTANCE) #裝所有道具
		while len(allItems) != 0:
			nearestItem = allItems[0]
			status = True
			for i in allPlayers:
				if i.effect == EffectType.PETRIFICATION or i.dead:
					continue
				if distance(i.position, nearestItem.position)/i.speed < distance(get_myself().position, nearestItem.position)/get_myself().speed and \
					distance(i.position, nearestItem.position) < 100:
					allItems.remove(nearestItem)
					status = False
					break
			if status == False:
				continue
			else:
				return nearestItem
		return None

	def EscapeTime(self, ghostPosition, ghostSpeed): # 鬼追到人的時間
		return distance_to(ghostPosition) / ghostSpeed

	def itemtime(self, ItemPosition, myspeed):
		return distance_to(ItemPosition) / myspeed
		
	def portkeytime(self, myspeed):
		allPortkey = get_portkeys(SortKey.DISTANCE)
		if len(allPortkey) == 0:
			return 1000
		return distance_to(get_portkeys(SortKey.DISTANCE)[0].position) / myspeed

	def player_tick(self) -> Vector2:
		myPosition = get_myself().position #我的位置
		myspeed = get_myself().speed #我的速度
		ghosts = get_ghosts()
		ghosts_position = [i.position for i in ghosts]
		to_ghosts = [distance_to(i.position) for i in ghosts]

		for i in range(len(ghosts)):
			if ghosts[i].chanting:
				ghosts_position[i] = ghosts[i].teleport_destination
				to_ghosts[i] = distance_to(ghosts[i].teleport_destination)
		
		ghostPosition = ghosts_position[to_ghosts.index(min(to_ghosts))]  #鬼的位置
		ghostSpeed = ghosts[to_ghosts.index(min(to_ghosts))].speed #鬼的速度
		EscapeTime = self.EscapeTime(ghostPosition, ghostSpeed) #鬼到我的時間
		portkeytime = self.portkeytime(myspeed)
		if myPosition == ghostPosition:
			return myPosition + myPosition.normalize()
		#分類帽:追鬼-------------------------------
		if get_myself().effect == EffectType.SORTINGHAT:
		#8秒 pass escape ghost
			if get_myself().effect_remain < EscapeTime:
				return self.escape(ghostPosition)
			else:
				return self.convert(ghostPosition)
		if get_myself().effect == EffectType.REMOVED_SORTINGHAT and get_myself().effect_remain > EscapeTime and self.nearest_reachable() != None:
			return self.convert(self.itemg())
		#-----------------------------------------
		#斗篷:躲鬼、追金探子------------------------
		if get_myself().effect == EffectType.CLOAK:
			if EscapeTime<60:
				return self.escape(ghostPosition)
			for i in get_items():
				if i.type == ItemType.GOLDEN_SNITCH:
					return i.position
		#-------------------------------------------
		item = self.nearest_reachable() # 最近距離可拿道具
		if item == None: #沒有道具
			return self.escape(ghostPosition)
		elif get_myself().dead == True: #有道具，我死了
			return self.itemg()
		else:
			item_type = item.type # 最近距離可拿道具的類型
			if item_type == ItemType.SORTINGHAT or item_type == ItemType.PATRONUS or item_type == ItemType.CLOAK: #最近的是否為保護型道具
				protectitemtime = self.itemtime(item.position, myspeed)#我到保護型道具的時間
			else:
				protectitemtime = 1000
			if distance(myPosition, ghostPosition) <= ghostSpeed*120: 
				if protectitemtime < EscapeTime : #可否拿道具避鬼
					return self.convert(self.itemg())
				elif portkeytime < EscapeTime:
					return get_portkeys(SortKey.DISTANCE)[0].position
				else:
					return self.escape(ghostPosition)
			else :
				return self.slow_convert(self.convert(self.itemg()))

