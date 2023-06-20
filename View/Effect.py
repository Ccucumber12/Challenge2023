import pygame
import random
from InstancesManager import get_game_engine
from InstancesManager import get_graphical_view
from EventManager.Events import EventInitialize, EventEveryTick
import Const

class Particle:
	def __init__(self, color, pos_x, pos_y):
		self.particles = []
		self.color = color
		self.x = pos_x
		self.y = pos_y

	def emit(self):
		view = get_graphical_view()
		if self.particles:
			self.delete()
			for particle in self.particles:
				particle[0][1] += particle[2][0]
				particle[0][0] += particle[2][1]
				particle[1] -= 0.2
				pygame.draw.circle(view.screen, pygame.Color(self.color),particle[0], int(particle[1]))
				

	def add(self):
		r = 10
		dir_x = random.randint(-3,3)
		dir_y = random.randint(-3,3)
		particle_circle = [[self.x,self.y],r,[dir_x,dir_y]]
		self.particles.append(particle_circle)
		
	def delete(self):
		particle_copy = [particle for particle in self.particles if particle[1] > 0]
		self.particles = particle_copy
		
	def tick(self):
		model = get_game_engine()
		if model.timer % 2 == 0:
			self.add()
		
		