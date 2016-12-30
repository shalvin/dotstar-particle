import array

def create_surface_int(width, height):
    return array.array('B', [0 for i in xrange(width * height * 4)])

def create_surface_float(width, height):
    newArray = array.array('f', [0.0 for i in xrange(width * height * 4)])
    for i in xrange(0, len(newArray), 4):
        newArray[i] = 1.0
    return newArray

def floats_to_ints(surface, width, height):
    return array.array('B', [int(surface[i] * 255) for i in xrange(width * height * 4)])

def get_pixel(surface, x, y, pitch):
    index = ((y * pitch) + x) * 4
    return (surface[index + 2], # R 
            surface[index + 3], # G
            surface[index + 1]) # B

def set_pixel(surface, x, y, pitch, r, g, b):
    index = ((y * pitch) + x) * 4
    surface[index]   = 1.0
    surface[index+1] = b
    surface[index+2] = r
    surface[index+3] = g
    return surface

def draw_line(surface, x, length, r, g, b):
    start = 4 * x
    end = 4 * (x + length)
    for i in xrange(start, end):    
        surface[i+1] = b
        surface[i+2] = r
        surface[i+3] = g
    return surface

def scale(surface, multiplier):
    for i in xrange(0, len(surface), 4):
        surface[i+1] *= multiplier
        surface[i+2] *= multiplier
        surface[i+3] *= multiplier
    return surface

def clear(surface, width, height):
    for i in xrange(0, len(surface), 4):
        surface[i+1] = 0
        surface[i+2] = 0
        surface[i+3] = 0
    return surface


class Surface:
    def __init__(self, width):
        self.width = width
        self.data = create_surface_float(width, 1)
        self.size = len(self.data)
    
    def clear(self):
        for i in xrange(0, self.size, 4):
            self.data[i+1] = 0
            self.data[i+2] = 0
            self.data[i+3] = 0

    def getPixel(self, x):
        index = (x) * 4
        return (self.data[index + 2], # R 
                self.data[index + 3], # G
                self.data[index + 1]) # B
    
    def setPixel(self, x, r, g, b):
        index = (x) * 4
        self.data[index]   = 1.0
        self.data[index+1] = b
        self.data[index+2] = r
        self.data[index+3] = g
    
    def drawLine(self, x, length, r, g, b):
        start = 4 * x
        end = 4 * (x + length)
        for i in xrange(start, end):    
            self.data[i+1] = b
            self.data[i+2] = r
            self.data[i+3] = g

    def scale(self, multiplier):
        for i in xrange(0, self.size, 4):
            self.data[i+1] *= multiplier
            self.data[i+2] *= multiplier
            self.data[i+3] *= multiplier

    def getIntArray(self):
        return array.array('B', [int(self.data[i] * 255) for i in xrange(self.size)])
    