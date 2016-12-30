import random
import colorsys
import time
import sched
from ParticleBase import Particle, ParticleSystem
from BounceParticle import BounceParticle
from util import clamp, average

class CountdownParticleSystem(ParticleSystem):
    def __init__(self, tickRate, strip, width, startTime, endTime):
        super(CountdownParticleSystem, self).__init__(tickRate, strip, width)
        self.startTime = startTime
        self.endTime = endTime
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.lastSecondUnit = int(time.time())
    
    def onUpdate(self, dt):
        timeRemaining = self.endTime - self.startTime
        currentTime = time.time()
        currentSecond = int(currentTime)
        if currentSecond != self.lastSecondUnit:
            self.lastSecondUnit = currentSecond
            self.addParticle(BounceParticle(0, 0, self))
        