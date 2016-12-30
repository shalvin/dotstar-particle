import random
import colorsys
import time
from ParticleBase import Particle, ParticleSystem
from util import clamp, average
from switchio import gpio_init
from threading import Lock

DETECTION_TIMEOUT = 3.0
DEBOUNCE = 0.2

class BpmParticleSystem(ParticleSystem):
    def __init__(self, tickRate, strip, width):
        super(BpmParticleSystem, self).__init__(tickRate, strip, width)
        self.timeSinceLastSpawn = 0.0
        self.persistenceMult = 0.9
        self.bpm = 85.0
        self.spawnPeriodMS = 1.0 / self.bpm * 60.0
        self.beatsPerMeasure = 4
        self.currentBeat = 1
        self.hue = random.random()
        
        self.lastPedalPressTime = time.time()
        self.lastPedalTimePeriods = []
        self.ioLock = Lock()
        gpio_init(self.io_callback)
    
    def onUpdate(self, dt):
        self.timeSinceLastSpawn += dt
        if self.timeSinceLastSpawn >= self.spawnPeriodMS:
            width = self.width
            if self.currentBeat == 1:
                self.hue = random.random()
                r,g,b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
                self.addParticle(BpmParticle(0, 0, 1, width / self.spawnPeriodMS, self.hue))
            elif self.currentBeat % 2 == 0:
                self.addParticle(BpmParticle(width - 1, 0, -1, width / self.spawnPeriodMS, self.hue))
            else:
                self.addParticle(BpmParticle(0, 0, 1, width / self.spawnPeriodMS, self.hue))
            self.timeSinceLastSpawn -= self.spawnPeriodMS

            self.currentBeat += 1
            if self.currentBeat > self.beatsPerMeasure:
                self.currentBeat = 1
    
    def reset(self):
        self.currentBeat = 1
        self.timeSinceLastSpawn = self.spawnPeriodMS
    
    def setBpm(self, bpm):
        if bpm > 400:
            return
        self.bpm = bpm
        self.spawnPeriodMS = 1.0 / self.bpm * 60.0
        
    def io_callback(self, channel):
        if self.ioLock.locked():
            return
        self.ioLock.acquire()
        currentTime = time.time()
        period = currentTime - self.lastPedalPressTime
        
        if period > DETECTION_TIMEOUT:
            self.lastPedalTimePeriods = []
            self.lastPedalPressTime = currentTime
            self.ioLock.release()
            return

        self.lastPedalPressTime = currentTime
        self.lastPedalTimePeriods.append(period)
        if len(self.lastPedalTimePeriods) > 4:
            del self.lastPedalTimePeriods[0]
        self.setBpm(60.0 / average(self.lastPedalTimePeriods))
        self.reset()
        self.ioLock.release()
        print "set %f, period %f" % (self.bpm, period)


class BpmParticle(Particle):
    def __init__(self, x, y, direction, velocity, hue):
        super(BpmParticle, self).__init__(x, y)
        self.direction = direction
        self.velocity = velocity
        h, s, v = (hue + random.uniform(-0.05, 0.05)) % 1.0, random.uniform(0.75, 1.0), 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        self.red = r
        self.green = g
        self.blue = b
        self.hueChangeRate = random.choice([1, -1]) * random.uniform(0.0005, 0.001)
    
    def onUpdate(self, dt):
        h,s,v = colorsys.rgb_to_hsv(self.red, self.green, self.blue)
        h = (h + self.hueChangeRate) % 1.0
        r,g,b = colorsys.hsv_to_rgb(h,s,v)
        self.red = r
        self.green = g
        self.blue = b


class FadeParticle(Particle):
    def __init__(self, x, hue, timeToLive):
        super(FadeParticle, self).__init__(x, 0)
        self.red, self.green, self.blue = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        self.timeToLive = timeToLive
        self.timeLeft = timeToLive
    
    def onUpdate(self, dt):
        self.timeLeft -= dt
        self.brightness = self.timeLeft / self.timeToLive
        if self.timeLeft < 0.0:
            self.alive = False

