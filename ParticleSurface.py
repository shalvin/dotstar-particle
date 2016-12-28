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