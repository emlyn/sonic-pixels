from bisect import bisect
from PIL import ImageColor

def getrgba(s):
    """Get an RGBA colour tuple from a string"""
    if s.lower() == 'transparent': # add a name for fully transparent
        s = '#0000'
    c = ImageColor.getrgb(s)
    if len(c) == 3:
        return c + (255,)
    return c

def _interpolate(vals, x):
    # handle out of range values
    if x < vals[0][0]:
        return vals[0][1]
    if x >= vals[-1][0]:
        return vals[-1][2]
    # get index in colour component map
    i = bisect(vals, [x])
    # if we are exactly on a value, return that
    if x == vals[i][0]:
        return vals[i][2]
    # otherwise interpolate between values on either side
    d0 = vals[i][0] - vals[i - 1][0]
    d1 = vals[i][1] - vals[i - 1][2]
    return int(vals[i - 1][2] + d1 * (x - vals[i - 1][0]) / d0)


class ColourScale:
    def __init__(self, cols):
        self.cols = cols

    def __call__(self, x):
        return tuple(_interpolate(col, x) for col in self.cols)

def scale(*args):
    """Get a colour scale, either by name or by building a scale from a list of points
    The magma, plasma, inferno & viridis scales are approximations of the equivalents from matplotlib"""
    if len(args) == 1:
        if isinstance(args[0], ColourScale):
            return args[0]
        try:
            return scales[args[0]]
        except KeyError:
            pass
    return _scale(*args)

def _scale(*args):
    """Build a colour scale from a list of colour points on the scale"""
    cols = [[], [], [], []]
    if len(args) == 1:
        # Make single colour be a constant scale
        args = args * 2
    # Populate known values
    for c in args:
        if isinstance(c, str):
            for i, v in enumerate(getrgba(c)):
                cols[i].append([None, v, v])
        elif len(c) == 1:
            for i, v in enumerate(getrgba(c[0])):
                cols[i].append([None, v, v])
        elif len(c) == 2:
            for i, v in enumerate(getrgba(c[1])):
                cols[i].append([c[0], v, v])
        else:
            for i, [v, w] in enumerate(zip(getrgba(c[1]), getrgba(c[2]))):
                cols[i].append([c[0], v, w])
    # Fill in missing range values
    for i in range(4):
        if cols[i][0][0] is None:
            cols[i][0][0] = 0
        if cols[i][-1][0] is None:
            cols[i][-1][0] = 1
        last = 0
        for j in range(1, len(cols[i])):
            if cols[i][j][0] is not None:
                if j > last + 1:
                    d = cols[i][j][0] - cols[i][last][0]
                    n = j - last
                    for k in range(last + 1, j):
                        cols[i][k][0] = cols[i][last][0] + d * (k - last) / n
                last = j
    # Find and remove redundant values
    for col in cols:
        j = 1
        while j < len(col) - 1:
            dv = col[j + 1][1] - col[j - 1][2]
            dx = col[j + 1][0] - col[j - 1][0]
            c = col[j-1][2] + (col[j][0] - col[j - 1][0]) * dv / dx
            if col[j][1] == col[j][2] and abs(c - col[j][1]) < 1:
                del col[j]
            else:
                j += 1
    return ColourScale(cols)

def show(*args):
    """Show a colour scale on screen"""
    from PIL import Image
    w = 1000
    h = 100
    sc = scale(*args)
    img = Image.new('RGBA', (w, h))
    pix = img.load()
    for x in range(w):
        c = sc(x/w)
        for y in range(h):
            pix[x, y] = c
    img.show()

scales = dict(flame=_scale('transparent', [0.4, 'red'], [0.7, 'yellow'], 'white'),
              magma=ColourScale([[[0, 0, 0],
                                  [0.1, 17, 17],
                                  [0.65, 238, 238],
                                  [0.9, 255, 255],
                                  [1, 252, 252]],
                                 [[0, 0, 0],
                                  [0.17, 17, 17],
                                  [0.25, 15, 15],
                                  [0.6, 76, 76],
                                  [1, 253, 253]],
                                 [[0, 3, 3],
                                  [0.055, 29, 29],
                                  [0.19, 107, 107],
                                  [0.23, 120, 120],
                                  [0.37, 130, 130],
                                  [0.7, 92, 92],
                                  [0.8, 112, 112],
                                  [1, 191, 191]],
                                 [[0, 255, 255],
                                  [1, 255, 255]]]),
              plasma=ColourScale([[[0, 12, 12],
                                   [0.01, 22, 22],
                                   [0.05, 42, 42],
                                   [0.5, 208, 208],
                                   [0.9, 254, 254],
                                   [1, 240, 240]],
                                  [[0, 7, 7],
                                   [0.2, 0, 0],
                                   [0.3, 9, 9],
                                   [1, 249, 249]],
                                  [[0, 135, 135],
                                   [0.04, 146, 146],
                                   [0.23, 169, 169],
                                   [0.94, 36, 36],
                                   [0.98, 39, 39],
                                   [0.99, 36, 36],
                                   [1, 33, 33]],
                                  [[0, 255, 255],
                                   [1, 255, 255]]]),
              inferno=ColourScale([[[0, 12, 12],
                                    [0.01, 22, 22],
                                    [0.05, 42, 42],
                                    [0.5, 208, 208],
                                    [0.9, 254, 254],
                                    [1, 240, 240]],
                                   [[0, 7, 7],
                                    [0.2, 0, 0],
                                    [0.3, 9, 9],
                                    [1, 249, 249]],
                                   [[0, 135, 135],
                                    [0.04, 146, 146],
                                    [0.2, 169, 169],
                                    [0.94, 36, 36],
                                    [0.98, 39, 39],
                                    [0.99, 36, 36],
                                    [1, 33, 33]],
                                   [[0, 255, 255],
                                    [1, 255, 255]]]),
              viridis=ColourScale([[[0, 68, 68],
                                    [0.1, 72, 72],
                                    [0.55, 30, 30],
                                    [0.65, 44, 44],
                                    [0.75, 85, 85],
                                    [1, 254, 254]],
                                   [[0, 1, 1],
                                    [0.4, 112, 112],
                                    [1, 231, 231]],
                                   [[0, 84, 84],
                                    [0.1, 121, 121],
                                    [0.5, 142, 142],
                                    [0.7, 104, 104],
                                    [0.95, 24, 24],
                                    [0.98, 28, 28],
                                    [1, 36, 36]],
                                   [[0, 255, 255],
                                    [1, 255, 255]]]))
