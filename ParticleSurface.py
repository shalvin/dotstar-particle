import array

def create_surface_int(width, height):
    return array.array('B', [0 for i in xrange(width * height * 4)])

def create_surface_float(width, height):
    return array.array('f', [0.0 for i in xrange(width * height * 4)])

def floats_to_ints(surface, width, height):
    return array.array('B', [int(surface[i] * 255) for i in xrange(width * height * 4)])

def get_pixel(surface, x, y, pitch):
    index = ((y * pitch) + x) * 4
    return (surface[index], 
            surface[index + 1],
            surface[index + 2])

def set_pixel(surface, x, y, pitch, r, g, b):
    index = ((y * pitch) + x) * 4
    surface[index]   = r
    surface[index+1] = g
    surface[index+2] = b
    return surface

def scale(surface, width, height, multiplier):
    for i in xrange(width * height * 4):
        surface[i] *= multiplier
    return surface

def clear(surface, width, height):
    for i in xrange(width * height * 4):
        surface[i] = 0
    return surface