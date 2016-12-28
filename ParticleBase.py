import ParticleSurface
import colorsys
import time

class ParticleSystem(object):
    def __init__(self, tickRate, strip, width):
        self.strip = strip
        self.particleList = []
        self.surface = ParticleSurface.create_surface_float(width, 1)
        self.aliveCount = 0
        self.width = width
        self.persistenceMult = 0.0
        self.strip.show(ParticleSurface.floats_to_ints(self.surface, width, 1))
        self.tickRate = tickRate
        self.lastUpdatedTime = time.time()

    def addParticle(self, particle):
        self.particleList.append(particle)
        self.aliveCount += 1
        particle.onCreate()

    def onUpdate(self, dt):
        pass

    def update(self, dt):
        currentTime = time.time()
        if currentTime < self.lastUpdatedTime + (1.0 / self.tickRate):
            return False
        updateDt = currentTime - self.lastUpdatedTime
        self.lastUpdatedTime = currentTime

        self.onUpdate(updateDt)
        for particle in self.particleList:
            particle.update(updateDt)
            if not particle.alive or (particle.x < self.width * -2 or particle.x > self.width * 2):
                self.aliveCount -= 1
                self.particleList.remove(particle)
        return True


    def render(self, hasTicked):
        width = self.width
        surface = ParticleSurface.scale(self.surface, self.persistenceMult)
        
        if hasTicked:
            for particle in self.particleList:
                prevX = int(particle.lastUpdateX)
                currX = int(particle.x)
                direction = particle.direction
                # In case the particle hasn't moved, fake a movement
                # (this will only draw one pixel)
                if currX == prevX:
                    currX += direction
                # Color all pixels between particle's last position and current position
                for x in xrange(prevX, currX, direction):
                    if x >= 0 and x < width:
                        r,g,b = ParticleSurface.get_pixel(surface, x, 0, width)
                        # Blend with current pixel colour using 'screen' mode
                        r = 1 - (1 - r) * (1 - particle.red)
                        g = 1 - (1 - g) * (1 - particle.green)
                        b = 1 - (1 - b) * (1 - particle.blue)
                        # Adjust brightness
                        h,l,s = colorsys.rgb_to_hls(r, g, b)
                        l *= particle.lum
                        r,g,b = colorsys.hls_to_rgb(h, l, s)
                        # Set new pixel colour
                        surface = ParticleSurface.set_pixel(surface, x, 0, width, r, g, b)

        self.strip.show(ParticleSurface.floats_to_ints(surface, width, 1))
        self.surface = surface


class Particle(object):
    def __init__(self, x, y):
        self.x = int(x)
        self.y = y
        self.velocity = 0.0
        self.direction = 1
        self.friction = 1.0
        self.size = 1.0
        self.brightness = 1.0
        self.lum = self.brightness
        self.flicker = 0.0
        self.fade = 0.0
        self.red = 1.0
        self.green = 1.0
        self.blue = 1.0
        self.alpha = 0.5
        self.alive = True
        self.lastUpdateX = 0
        self.lastUpdateY = 0

    def update(self, dt):
        self.lastUpdateX = self.x
        self.lastUpdateY = self.y
        self.x += self.direction * self.velocity * dt
        self.velocity *= self.friction
        self.lum = self.brightness
        if self.flicker != 0.0:
            self.lum += (1 + random.uniform(-self.flicker, self.flicker)) * self.brightness
        
        self.onUpdate(dt)
    
    def onUpdate(self, dt):
        pass

    def onCreate(self):
        pass
