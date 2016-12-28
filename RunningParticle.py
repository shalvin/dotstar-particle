import random
import colorsys
from ParticleBase import Particle, ParticleSystem
from util import clamp


class RunningParticleSystem(ParticleSystem):
    def __init__(self, strip, width):
        super(RunningParticleSystem, self).__init__(strip, width)
        self.spawnPeriodMS = 2
        self.timeSinceLastSpawn = 0.0
        self.persistenceMult = 0.9

    def onUpdate(self, dt):
        if self.timeSinceLastSpawn > self.spawnPeriodMS:
            self.addParticle(RunningParticle(0, 0, 1))
            self.timeSinceLastSpawn = 0.0
        self.timeSinceLastSpawn += dt

class RunningParticle(Particle):
    def __init__(self, x, y, direction):
        super(RunningParticle, self).__init__(x, y)
        self.direction = direction
        self.velocity = direction * random.uniform(40, 60)
        self.friction = random.uniform(1.0015, 1.015)
        h, s, v = random.random(), random.uniform(0.75, 1.0), random.uniform(0.0, 0.01)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        self.red = r
        self.green = g
        self.blue = b
        self.hueChangeRate = random.choice([1, -1]) * random.uniform(0.001, 0.015)
        self.valueChangeRate = random.uniform(0.005, 0.01)
    
    def onUpdate(self, dt):
        h,s,v = colorsys.rgb_to_hsv(self.red, self.green, self.blue)
        h = (h + self.hueChangeRate) % 1.0
        if v < 1.0:
            v = clamp(v + self.valueChangeRate, 0.0, 1.0)
        r,g,b = colorsys.hsv_to_rgb(h,s,v)
        self.red = r
        self.green = g
        self.blue = b

