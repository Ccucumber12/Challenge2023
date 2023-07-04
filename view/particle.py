import random

import pygame as pg

import const
from utl import random_fluctuation


class GatheringParticleEffect:
    """
    Create a particle effect of circles gathering to a point, 
    representing ghost's teleport chanting effect.

    The number of particles will increase as the chanting time goes on.
    """

    def __init__(self, position: pg.Vector2, alive_time, color: pg.Color = None) -> None:
        self.position = position
        self.particles: list[Particle] = []
        self.particle_number = random.randint(9, 11)
        self.alive_time = alive_time
        self.color = color
        self.counter = 0
        for _ in range(self.particle_number):
            self.particles.append(Particle(position, self.color))

    def tick(self) -> None:
        remain_particles = []
        for particle in self.particles:
            particle.update()
            if particle.arrive():
                self.particle_number -= 1
            else:
                remain_particles.append(particle)
        self.particles = remain_particles
        for _ in range(self.counter // 25):
            if random.random() >= 0.2:
                self.particles.append(Particle(self.position, self.color))
                self.particle_number += 1
        self.counter += 1


class CastMagicParticleEffect:
    """
    Create a shooting particle effect inside a segment. 
    """

    def __init__(self, attacker, victim, speed: int, color: pg.Color = None, thickness = 5) -> None:
        self.current_position = pg.Vector2(attacker.position)
        self.victim = victim
        self.speed = speed
        self.color = color
        self.thickness = thickness
        self.particles = []
    
    def tick(self) -> bool:
        """
        Return true if magic hit victim.
        """
        remain_particles = []
        for particle in self.particles:
            particle.update()
            if not particle.arrive():
                remain_particles.append(particle)
        self.particles = remain_particles

        for _ in range(int(random_fluctuation(self.thickness))):
            self.particles.append(Particle(self.current_position, self.color, const.PETRIFICATION_ANIMATION_PARTICLE_RADIUS))
        self.current_position += (self.victim.position - self.current_position).normalize() * self.speed
        return (self.current_position - self.victim.position).length() <= 5


class Particle:
    def __init__(self, position: pg.Vector2, color: pg.Color = None, radius: float = 5):
        self.speed = random.randint(50, 300)
        self.displacement = pg.Vector2.from_polar((
            random.choice([1, -1]) * random.uniform(2 * self.speed / const.FPS, 40),
            random.random() * 360))
        self.destination = position
        self.position: pg.Vector2 = position + self.displacement
        if color == None:
            self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        else:
            color_random_range = 50
            self.color = pg.Color(color)
            for i in range(3):
                self.color[i] += max(0, min(255, random.randint(-color_random_range, color_random_range)))
        self.radius = radius * ((random.random() - 0.5) * 0.2 + 1)

    def update(self):
        self.position = self.position - self.displacement.normalize() * self.speed / const.FPS

    def arrive(self) -> bool:
        if (self.destination - self.position).length() < 2 * self.speed / const.FPS:
            return True
        return False
