#!/usr/bin/python

import sys
import time
import random
import time
from switchio import gpio_cleanup
from ParticleBase import ParticleSystem
from RunningParticle import RunningParticle, RunningParticleSystem
from BpmParticle import BpmParticle, BpmParticleSystem
from CountdownParticle import CountdownParticleSystem
from dotstar import Adafruit_DotStar

NUM_PIXELS = 120 # Number of LEDs in strip

# Here's how to control the strip from any two GPIO pins:
DATAPIN   = 10
CLOCKPIN  = 11

FPS = 120.0

s_strip = Adafruit_DotStar()
s_run = True
s_particleSystems = [CountdownParticleSystem(FPS / 1.0, s_strip, NUM_PIXELS)]

def initStrip():
    s_strip.begin()
    s_strip.setBrightness(255)

def stripLoop():
    lastFrameTime = time.time()
    while s_run:
        currentTime = time.time()
        dt = currentTime - lastFrameTime
        lastFrameTime = currentTime

        sleepTime = 1 / FPS - dt
        if sleepTime > 0.0:
            time.sleep(sleepTime)

        global s_particleSystems
        for system in s_particleSystems:
            system.render(system.update(dt))
        

###############################################################################

initStrip()

try:
    import cProfile
    if len(sys.argv) > 1 and sys.argv[1] == '--profile':
        cProfile.run('stripLoop()')
    else:
        stripLoop()
except KeyboardInterrupt:
    gpio_cleanup()
