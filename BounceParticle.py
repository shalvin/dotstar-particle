import random
import colorsys
from ParticleBase import Particle
from util import clamp

class BounceParticle(Particle):
    def __init__(self, x, y, parentSystem):
        super(BounceParticle, self).__init__(x, y)
        self.parentSystem = parentSystem
        self.velocity = 4
        h, s, v = random.random(), 1.0, 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        self.red = r
        self.green = g
        self.blue = b
        self.hueChangeRate = random.uniform(0.001, 0.01)

    def onUpdate(self):
        if self.x < 0 or self.x > NUM_PIXELS:
            self.direction *= -1
        global s_t
        global s_surfacePersistenceMult
        s_surfacePersistenceMult = clamp(math.fabs(math.sin(s_t/128)), 0.5, 1.0)
        h,s,v = colorsys.rgb_to_hsv(self.red, self.green, self.blue)
        h += self.hueChangeRate + random.uniform(0.0, self.hueChangeRate)
        r,g,b = colorsys.hsv_to_rgb(h,s,v)
        self.red = r
        self.green = g
        self.blue = b
