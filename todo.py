import ParticleBase

class ExplodedParticle(Particle):
	def __init__(self, x, y, direction, r, g, b):
		super(ExplodedParticle, self).__init__(x, y)
		# self.fade = random.uniform(0.1, 0.2)
		# self.flicker = random.uniform(0.3, 0.5)
		self.direction = direction
		self.velocity = self.direction * random.uniform(3.0, 5.0)
		self.friction = random.uniform(0.8, 0.95)
		self.alpha = 0.5
		global s_t
		self.deathTime = s_t + random.randint(20, 50)
		if (r,g,b) != (1,1,1):
			h,l,s = colorsys.rgb_to_hls(r,g,b)
			h = clamp(h + random.uniform(-0.2, 0.2), 0.0, 1.0)
			l = 1.0
			s = random.uniform(0.8, 1.0)
			r,g,b = colorsys.hls_to_rgb(h,l,s)
		self.red = r
		self.green = g
		self.blue = b

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
		self.red = r
		self.green = g
		self.blue = b
		# self.fade = random.uniform(0.1, 0.2)
		# self.flicker = random.uniform(0.0, 0.1)
	
	def onUpdate(self):
		if self.x >= NUM_PIXELS:
			self.alive = False
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, -1, self.color))
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, -1, self.color))
			self.particleSystem.addParticle(ExplodedParticle(self.x, self.y, -1, self.color))