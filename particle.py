#!/usr/bin/python

import sys
import time
import random
import math
import colorsys
import copy
from dotstar import Adafruit_DotStar

NUM_PIXELS = 120 # Number of LEDs in strip

# Here's how to control the strip from any two GPIO pins:
DATAPIN   = 10
CLOCKPIN  = 11

s_strip     = Adafruit_DotStar(NUM_PIXELS, DATAPIN, CLOCKPIN)
s_run 		= True
s_particleSystems = []
s_surfacePersistenceMult = 0.85
s_t = 0

def initStrip():
	s_strip.begin()
	s_strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle
	s_strip.clear()


def stripLoop():
	while s_run:
		for system in s_particleSystems:
			if random.randint(0, 50) == 0:
				system.addParticle(FireworkParticle(random.randint(50, 70), 0, random.choice([1, -1]), system))
			system.update()
		for system in s_particleSystems:
			system.render()
		global s_t
		s_t += 1
		
def alphaBlendColor(newColor, oldColor, alpha):
	r = (alpha * newColor.red) + ((1.0 - alpha) * oldColor.red)
	g = (alpha * newColor.green) + ((1.0 - alpha) * oldColor.green)
	b = (alpha * newColor.blue) + ((1.0 - alpha) * oldColor.blue)
	return RGB(r, g, b)

def colorFloatToInt(colorFloat):
	return int(colorFloat * 255)

def colorToRgbInt(color):
	return (colorFloatToInt(color.red) << 16) | (colorFloatToInt(color.green) << 8) | (colorFloatToInt(color.blue))

	
def renderStrip(surface, strip, w, h):
	for i in range(w):
		for j in range(h):
			c = surface.getPixel(i, j)
			strip.setPixelColor(i, c.rgbInt)
	strip.show()


class RGB:
	def __init__(self, r, g, b):
		self.red = r
		self.green = g
		self.blue = b
		self.rgbInt = colorToRgbInt(self)

	def GetRGBWithLuminanceMod(self, luminanceMod):
		h,l,s = colorsys.rgb_to_hls(self.red, self.green, self.blue)
		l *= luminanceMod
		r,g,b = colorsys.hls_to_rgb(h, l, s)
		return RGB(r, g, b)

class Surface:
	def __init__(self, width, height):
		self.w = width
		self.h = height
		self.data = [[RGB(0, 0, 0) for i in range(self.h)] for j in range(self.w)]

	def getPixel(self, x, y):
		return self.data[x][y]

	def setPixel(self, x, y, r, g, b):
		if x > self.w or y > self.h:
			return
		self.data[x][y] = RGB(r, g, b)
	
	def clear(self):
		for i in range(self.w):
			for j in range(self.h):
				self.data[i][j].red = 0
				self.data[i][j].green = 0
				self.data[i][j].blue = 0

	def applyLuminanceMod(self, luminance):
		for i in range(self.w):
			for j in range(self.h):
				c = self.getPixel(i, j)
				l = c.GetRGBWithLuminanceMod(luminance)
				self.setPixel(i, j, l.red, l.green, l.blue)

class Particle(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.velocity = 0.0
		self.friction = 1.0
		self.size = 1.0
		self.brightness = 1.0
		self.lum = self.brightness
		self.flicker = 0.0
		self.fade = 0.0
		self.color = RGB(1, 1, 1)
		self.alpha = 0.5
		self.alive = True

	def update(self):
		self.x += self.velocity
		self.brightness -= self.fade
		self.lum = self.brightness
		if self.flicker != 0.0:
			self.lum += (1 + random.uniform(-self.flicker, self.flicker)) * self.brightness
		self.velocity *= self.friction
		self.onUpdate()
	
	def onUpdate(self):
		pass

class ParticleSystem:
	def __init__(self):
		self.particleList = []
		self.surface = Surface(NUM_PIXELS, 1)

	def addParticle(self, particle):
		self.particleList.append(particle)

	def update(self):
		aliveCount = len(self.particleList)
		for particle in self.particleList:
			particle.update()
			if not particle.alive:
				aliveCount -= 1
				self.particleList.remove(particle)
		if aliveCount <= 0:
			return False
			print "system dwon"
		return True

	def render(self):
		# self.surface.clear()
		self.surface.applyLuminanceMod(s_surfacePersistenceMult)
		for p in self.particleList:
			self.particleRender(p)
		renderStrip(self.surface, s_strip, NUM_PIXELS, 1)
		
	def particleRender(self, particle):
		x = int(math.floor(particle.x))
		y = int(math.floor(particle.y))
		if x < 0 or y < 0 or x >= self.surface.w or y >= self.surface.h:
			particle.alive = False
			return
		lum = particle.lum if particle.lum > 0 else 0
		alphaX = (1 - (particle.x % 1)) * lum
		xSpill = (particle.x % 1) * lum
		
		oldColor = self.surface.getPixel(x, y)
		c = particle.color
		cLum = c.GetRGBWithLuminanceMod(alphaX)
		cLum = alphaBlendColor(cLum, oldColor, particle.alpha)
		self.surface.setPixel(x, y, cLum.red, cLum.green, cLum.blue)

		if x >= self.surface.w - 2:
			return
		oldSpillColor = self.surface.getPixel(x + 1, y)
		cSpill = particle.color
		cLum = cSpill.GetRGBWithLuminanceMod(xSpill)
		cLum = alphaBlendColor(cLum, oldSpillColor, particle.alpha)
		self.surface.setPixel(x + 1, y, cLum.red, cLum.green, cLum.blue)


###############################################################################


class ExplodedParticle(Particle):
	def __init__(self, x, y, direction):
		super(ExplodedParticle, self).__init__(x, y)
		self.fade = random.uniform(0.1, 0.2)
		self.flicker = random.uniform(0.1, 0.2)
		self.velocity = direction * random.uniform(2.2, 4.4)
		self.friction = random.uniform(0.95, 1.0)
		self.alpha = 0.2
		global s_t
		self.deathTime = s_t + random.randint(15, 30)

	def onUpdate(self):
		if s_t > self.deathTime:
			self.alive = False

class FireworkParticle(Particle):
	s_minNumExplode = 1
	s_maxNumExplode = 3

	def __init__(self, x, y, direction, particleSystem):
		super(FireworkParticle, self).__init__(x, y)
		self.particleSystem = particleSystem
		self.velocity = direction * random.uniform(0.5, 2.5)
		self.friction = random.uniform(0.95,1.0)
		h, s, v = random.random(), random.uniform(0.8, 1.0), 1.0
		r, g, b = colorsys.hsv_to_rgb(h, s, v)
		self.color.red = r
		self.color.green = g
		self.color.blue = b
		self.fade = random.uniform(0.01, 0.05)
		self.flicker = random.uniform(0.0, 0.1)
		global s_t
		self.deathTime = s_t + random.randint(10, 60)
	
	def onUpdate(self):
		global s_t
		if s_t > self.deathTime:
			self.alive = False
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, 1))
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, -1))

###############################################################################

initStrip()

system = ParticleSystem()
s_particleSystems.append(system)

for i in range(0, 10):
	p = FireworkParticle(random.randint(50, 70), 0, random.choice([1, -1]), system)
	system.addParticle(p)


# p = FireworkParticle(0, 0, system)
# system.addParticle(p)

# p = Particle(30, 0)
# p.velocity = 2
# p.color.green = 0
# system.addParticle(p)
# p = Particle(90, 0)
# p.color.red = 0
# p.velocity = -2
# system.addParticle(p)

import cProfile
if len(sys.argv) > 1 and sys.argv[1] == '--profile':
	cProfile.run('stripLoop()')
else:
	stripLoop()
