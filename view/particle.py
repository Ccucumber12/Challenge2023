import pygame as pg
import random

import const

class GatheringParticleEffect:
    """
    Create a particle effect of circles gathering to a point, 
    representing ghost's teleport chanting effect.

    The number of particles will increase as the chanting time goes on.
    """

    def __init__(self, position: pg.Vector2, alive_time) -> None:
        self.position = position
        self.particles: list[Particle] = []
        self.particle_number = random.randint(9, 11)
        self.alive_time = alive_time
        for _ in range(self.particle_number):
            self.particles.append(Particle(position))

    def tick(self) -> None:
        arrived_particle: list[Particle] = []
        for particle in self.particles:
            particle.update()
            if particle.arrive():
                arrived_particle.append(particle)
                self.particle_number -= 1
        self.particles = [x for x in self.particles if x not in arrived_particle]
        for _ in range(2 * len(arrived_particle)):
            if self.particle_number > 15:
                break
            if random.random() >= 0.4:
                self.particles.append(Particle(self.position))
                self.particle_number += 1


class Particle:
    def __init__(self, position: pg.Vector2):
        self.speed = random.randint(50, 300)
        self.displacement = pg.Vector2((
            random.choice([1, -1]) * random.uniform(5 * self.speed / const.FPS, 50),
            random.choice([1, -1]) * random.uniform(5 * self.speed / const.FPS, 50)))
        self.destination = position
        self.position: pg.Vector2 = position + self.displacement
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.radius = random.uniform(3, 10)

    def update(self):
        self.position = self.position - self.displacement.normalize() * self.speed / const.FPS

    def arrive(self) -> bool:
        if (self.destination - self.position).length() < 2 * self.speed / const.FPS:
            return True
        return False
