def clamp(value, lower, upper):
    return max(min(value, upper), lower)

def average(l):
    return sum(l) / float(len(l))
    