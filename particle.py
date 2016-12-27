#!/usr/bin/python

import sys
import time
import random
import math
import colorsys
import copy
import ParticleSurface
from dotstar import Adafruit_DotStar

NUM_PIXELS = 120 # Number of LEDs in strip

# Here's how to control the strip from any two GPIO pins:
DATAPIN   = 10
CLOCKPIN  = 11

MODEDURATION = 1000
DEFAULT_PERSISTENCE = 0.9

MODE_FULLRUN 	= 1
MODE_FIREWORK	= 2
MODE_BOUNCE		= 3

s_strip     = Adafruit_DotStar(12000000)
s_run 		= True
s_particleSystems = []
s_surfacePersistenceMult = DEFAULT_PERSISTENCE
s_t = 0
s_modeCycle = [MODE_FULLRUN, MODE_BOUNCE]
s_mode = 0
s_modeTimeout = MODEDURATION
s_nextParticleSpawn = 0

def initStrip():
	s_strip.begin()
	s_strip.setBrightness(255)

def stripLoop():
	while s_run:
		global s_modeCycle
		global s_modeTimeout
		global s_mode
		global s_t
		global s_surfacePersistenceMult
		if s_t > s_modeTimeout:
			s_modeTimeout = s_t + MODEDURATION
			s_mode = (s_mode + 1) % len(s_modeCycle)
			s_surfacePersistenceMult = DEFAULT_PERSISTENCE
			for system in s_particleSystems:
				system.particleList = []

		global s_nextParticleSpawn
		s_nextParticleSpawn -= 1
		currentMode = s_modeCycle[s_mode]
		for system in s_particleSystems:
			if currentMode == MODE_FULLRUN and s_nextParticleSpawn <= 0:
				system.addParticle(FullRunParticle(0, 0, 1))
				s_nextParticleSpawn = random.randint(25,50)
			if currentMode == MODE_FIREWORK and random.randint(0, 50) == 0:
				system.addParticle(FireworkParticle(0, 0, 1, system))
			if currentMode == MODE_BOUNCE and len(system.particleList) < 2:
				system.addParticle(BounceParticle(0, 0, system))
				system.addParticle(BounceParticle(NUM_PIXELS - 1, 0, system))				
			system.update()
		for system in s_particleSystems:
			system.render()
		s_t += 1
		
def blendAdditive(newColor, oldColor, alpha):
	return (alpha * newColor) + ((1.0 - alpha) * oldColor)

def blendScreen(newColor, oldColor, alpha):
	return 1 - (1 - oldColor) * (1 - newColor)

def alphaBlendColor(newColor, oldColor, alpha):
	r = blendScreen(newColor.red, oldColor.red, alpha)
	g = blendScreen(newColor.green, oldColor.green, alpha)
	b = blendScreen(newColor.blue, oldColor.blue, alpha)
	return RGB(r, g, b)

def colorFloatToInt(colorFloat):
	return int(colorFloat * 255)

def colorToRgbInt(color):
	return (colorFloatToInt(color.red) << 16) | (colorFloatToInt(color.green) << 8) | (colorFloatToInt(color.blue))

def clamp(value, lower, upper):
	return max(min(value, upper), lower)

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

class Particle(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.velocity = 0.0
		self.direction = 1
		self.friction = 1.0
		self.size = 1.0
		self.brightness = 1.0
		self.lum = self.brightness
		self.flicker = 0.0
		self.fade = 0.0
		self.color = RGB(1, 1, 1)
		self.alpha = 0.5
		self.alive = True
		self.lastUpdateX = 0
		self.lastUpdateY = 0

	def update(self):
		self.lastUpdateX = self.x
		self.lastUpdateY = self.y
		self.x += self.direction * self.velocity
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
		self.surface = ParticleSurface.create_surface_float(NUM_PIXELS, 1)
		self.aliveCount = 0

	def addParticle(self, particle):
		self.particleList.append(particle)
		self.aliveCount += 1

	def update(self):
		for particle in self.particleList:
			particle.update()
			if not particle.alive:
				self.aliveCount -= 1
				self.particleList.remove(particle)
		if self.aliveCount <= 0:
			return False
		return True

	def render(self):
		width = NUM_PIXELS
		surface = ParticleSurface.scale(self.surface, width, 1, s_surfacePersistenceMult)

		for particle in self.particleList:
			# Color all pixels between particle's last position and current position
			for x in xrange(int(particle.lastUpdateX), int(particle.x), particle.direction):
				if x >= 0 and x < width - 1:
					r,g,b = ParticleSurface.get_pixel(surface, x, 0, width)
					# Blend with current pixel colour using 'screen' mode
					particleColor = particle.color
					r = 1 - (1 - r) * (1 - particleColor.red)
					g = 1 - (1 - g) * (1 - particleColor.green)
					b = 1 - (1 - b) * (1 - particleColor.blue)
					# Adjust brightness
					h,l,s = colorsys.rgb_to_hls(r, g, b)
					l *= particle.lum
					r,g,b = colorsys.hls_to_rgb(h, l, s)
					# Set new pixel colour
					surface = ParticleSurface.set_pixel(surface, x, 0, width, r, g, b)

		s_strip.show(ParticleSurface.floats_to_ints(surface, width, 1))

		
###############################################################################


class ExplodedParticle(Particle):
	def __init__(self, x, y, direction, color):
		super(ExplodedParticle, self).__init__(x, y)
		# self.fade = random.uniform(0.1, 0.2)
		# self.flicker = random.uniform(0.3, 0.5)
		self.direction = direction
		self.velocity = self.direction * random.uniform(3.0, 5.0)
		self.friction = random.uniform(0.8, 0.95)
		self.alpha = 0.5
		global s_t
		self.deathTime = s_t + random.randint(20, 50)
		r,g,b = color.red, color.green, color.blue
		if (r,g,b) != (1,1,1):
			h,l,s = colorsys.rgb_to_hls(r,g,b)
			h = clamp(h + random.uniform(-0.2, 0.2), 0.0, 1.0)
			l = 1.0
			s = random.uniform(0.8, 1.0)
			r,g,b = colorsys.hls_to_rgb(h,l,s)
		self.color.red = r
		self.color.green = g
		self.color.blue = b

	def onUpdate(self):
		global s_t
		if s_t > self.deathTime:
			self.alive = False

class FireworkParticle(Particle):
	def __init__(self, x, y, direction, particleSystem):
		super(FireworkParticle, self).__init__(x, y)
		self.particleSystem = particleSystem
		self.alpha = 0.9
		self.direction = direction
		self.velocity = self.direction * random.uniform(2, 2.5)
		h, s, v = random.random(), 1.0, 1.0
		r, g, b = colorsys.hsv_to_rgb(h, s, v)
		self.color.red = r
		self.color.green = g
		self.color.blue = b
		# self.fade = random.uniform(0.1, 0.2)
		# self.flicker = random.uniform(0.0, 0.1)
	
	def onUpdate(self):
		if self.x >= NUM_PIXELS:
			self.alive = False
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, -1, self.color))
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, -1, self.color))
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, -1, self.color))

class FullRunParticle(Particle):
	def __init__(self, x, y, direction):
		super(FullRunParticle, self).__init__(x, y)
		self.direction = direction
		self.velocity = direction * random.uniform(2.1, 8.1)
		h, s, v = random.random(), 1.0, 1.0
		r, g, b = colorsys.hsv_to_rgb(h, s, v)
		self.color.red = r
		self.color.green = g
		self.color.blue = b

class BounceParticle(Particle):
	def __init__(self, x, y, parentSystem):
		super(BounceParticle, self).__init__(x, y)
		self.parentSystem = parentSystem
		self.velocity = 4
		h, s, v = random.random(), 1.0, 1.0
		r, g, b = colorsys.hsv_to_rgb(h, s, v)
		self.color.red = r
		self.color.green = g
		self.color.blue = b
		self.hueChangeRate = random.uniform(0.001, 0.01)

	def onUpdate(self):
		if self.x < 0 or self.x > NUM_PIXELS:
			self.direction *= -1
		global s_t
		global s_surfacePersistenceMult
		s_surfacePersistenceMult = clamp(math.fabs(math.sin(s_t/128)), 0.5, 1.0)
		h,s,v = colorsys.rgb_to_hsv(self.color.red, self.color.green, self.color.blue)
		h += self.hueChangeRate + random.uniform(0.0, self.hueChangeRate)
		r,g,b = colorsys.hsv_to_rgb(h,s,v)
		self.color.red = r
		self.color.green = g
		self.color.blue = b

###############################################################################

initStrip()

system = ParticleSystem()
s_particleSystems.append(system)

p = FireworkParticle(0, 0, 1, system)
system.addParticle(p)

import cProfile
if len(sys.argv) > 1 and sys.argv[1] == '--profile':
	cProfile.run('stripLoop()')
else:
	stripLoop()
