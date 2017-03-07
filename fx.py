import colour
from PIL import Image, ImageColor
from bisect import bisect_right
from math import exp, sqrt
from numbers import Number
from random import choice, random, randrange


def gradient(size, colours):
    img = Image.new('RGBA', size)
    pix = img.load()
    if len(colours) == 0:
        colours = ['black']
    scale = colour.scale(*colours)
    for x in range(size[0]):
        c = scale(x / (size[0] - 1.0))
        for y in range(size[1]):
            pix[x, y] = c
    return img


class FXBase(object):
    def __init__(self, size):
        self.start_time = None
        self.size = size

    def start(self, start_time):
        self.start_time = start_time

    def getDisplay(self, time, previous):
        raise NotImplementedError("FX implementations must implement getDisplay")


class SolidFX(FXBase):
    def __init__(self, size, *colours):
        super().__init__(size)
        self.img = gradient(size, colours)

    def getDisplay(self, time, previous):
        return self.img


class FadeFX(FXBase):
    def __init__(self, size, *vals):
        super().__init__(size)
        self.start_t = None
        self.start_img = None
        self.imgs = []
        cols = []
        tlast = 0
        for v in vals:
            if isinstance(v, Number):
                if len(cols) == 0 and len(self.imgs) == 0:
                    img = None
                else:
                    img = gradient(size, cols)
                self.imgs.append([tlast, img])
                tlast += v
                cols = []
            else:
                cols.append(v)
        self.imgs.append([tlast, gradient(size, cols)])

    def getDisplay(self, time, previous):
        if self.start_t is None:
            self.start_t = time
        if self.imgs[0][1] is None:
            if previous is None:
                self.imgs[0][1] = gradient(self.size, [])
            else:
                self.imgs[0][1] = previous
        if time <= self.start_t:
            return self.imgs[0][1]
        elif time >= self.start_t + self.imgs[-1][0]:
            return self.imgs[-1][1]
        i = bisect_right(self.imgs, [time - self.start_t, None])
        a = (time - self.start_t - self.imgs[i-1][0]) / (self.imgs[i][0] - self.imgs[i-1][0])
        return Image.blend(self.imgs[i-1][1], self.imgs[i][1], a)


class ChaseFX(FXBase):
    def __init__(self, size, *args):
        self.start_t = None
        self.size = size
        if len(args) > 0 and isinstance(args[0], Number):
            self.time = args[0]
            args = args[1:]
        else:
            self.time = 1
        if len(args) > 0 and isinstance(args[0], Number):
            self.width = args[0]
            args = args[1:]
        else:
            self.width = max(size[0] // 10, 4)
        if len(args) > 0 and isinstance(args[0], Number):
            self.fade = args[0]
            args = args[1:]
        else:
            self.fade = int(sqrt(max(self.width, 0) / 1.5))
        self.sprite = gradient((self.width, size[1]), args if len(args) > 0 else ['white'])
        pix = self.sprite.load()
        for x in range(min(self.fade, (self.width + 1) // 2)):
            v = (x + 1) / (self.fade + 1)
            for y in range(size[1]):
                p = pix[x, y]
                pix[x, y] = p[0:3] + (int(p[3] * v),)
                if x < self.width // 2:
                    # Dont double-fade central pixel on odd widths
                    p = pix[self.width - 1 - x, y]
                    pix[self.width - 1 - x, y] = p[0:3] + (int(p[3] * v),)

    def getDisplay(self, time, previous):
        if self.start_t is None:
            self.start_t = time
        if time > self.start_t + abs(self.time):
            return None
        img = Image.new('RGBA', self.size, (0, 0, 0, 0))
        a = (time - self.start_t) / abs(self.time)
        if self.time < 0:
            a = 1 - a
        x = round(a * (self.size[0] + self.width) - self.width)
        img.paste(self.sprite, (x, 0))
        return img


class FlashFX(FXBase):
    def __init__(self, size, *args):
        super().__init__(size)
        self.start_t = None
        if len(args) > 0 and isinstance(args[0], Number):
            self.time = args[0]
            args = args[1:]
        else:
            self.time = 0
        self.img = gradient(size, args)
        self.trans = Image.new('RGBA', size, (0, 0, 0, 0))

    def getDisplay(self, time, previous):
        if self.start_t is None:
            self.start_t = time
        if time > self.start_t + self.time:
            return None
        if self.time <= 0:
            return self.img
        a = (time - self.start_t) / self.time
        return Image.blend(self.img, self.trans, a)


class SparkleFX(FXBase):
    def __init__(self, size, *args):
        super().__init__(size)
        self.start_t = None
        self.prev_t = None
        if len(args) > 0 and isinstance(args[0], Number):
            self.time = args[0]
            args = args[1:]
        else:
            self.time = 0
        if len(args) > 0 and isinstance(args[0], Number):
            self.fade = args[0]
            args = args[1:]
        else:
            self.fade = 0
        if len(args) > 0 and isinstance(args[0], Number):
            self.nspark = args[0]
            args = args[1:]
        else:
            self.nspark = 10
        self.colours = [ImageColor.getrgb(c) for c in (args if len(args) > 0 else ['white'])]
        self.img = Image.new('RGBA', size, (0, 0, 0, 0))
        self.trans = Image.new('RGBA', size, (0, 0, 0, 0))

    def getDisplay(self, time, previous):
        if self.start_t is None:
            self.start_t = time
        if time > self.start_t + self.time + self.fade:
            return None
        pix = self.img.load()
        if self.prev_t is not None:
            nfade = 255 if self.fade <= 0 else round(255 * (time - self.prev_t) / self.fade)
            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    p = pix[x, y]
                    pix[x, y] = p[:3] + (max(0, p[3] - nfade),)
        if time < self.start_t + self.time:
            for i in range(self.nspark):
                pix[randrange(self.size[0]), randrange(self.size[1])] = choice(self.colours)
        self.prev_t = time
        return self.img


class FlameFX(FXBase):
    EXTRA = 10 # Extra pixels before start of strip where sparks are generated
    # Adapted from https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/#fire
    def __init__(self, size, *args):
        super().__init__(size)
        self.flame = [0.0] * (size[0] + FlameFX.EXTRA)
        self.sparking = args[0] if len(args) > 0 else 1 # Average number of sparks per frame
        self.cooling = args[1] if len(args) > 1 else 1 # Cooling rate
        self.kernel = self.parse_kernel(args[2]) if len(args) > 2 else [0, 1, 2] # Drift + diffusion
        self.palette = colour.scale('flame')

    def parse_kernel(self, s):
        return [int(c) for c in s]

    def nsparks(self):
        # Poisson distributed random number with mean self.sparking
        l = exp(-self.sparking)
        k = 0
        p = 1
        while p > l:
            k += 1
            p *= random()
        return k - 1

    def getDisplay(self, time, previous):
        f = self.flame
        # Cool down every cell a little
        for i in range(len(self.flame)):
            f[i] -= random() * 3 * self.cooling / len(f)
            if f[i] < 0.0:
                # Clamp pixel heat to minimum of 0
                f[i] = 0.0
        # Heat from each cell drifts 'up' and diffuses a little
        for i in reversed(range(1, len(f))):
            n = 0
            s = 0
            for k, v in enumerate(self.kernel):
                if i - k >= 0:
                    n += v
                    s += v * f[i - k]
            f[i] = s / n if n > 0 else 0
        # Randomly ignite new 'sparks' off the end of the strip
        for i in range(self.nsparks()):
            # Pick a random pixel in the off-strip area
            pos = int(random() * FlameFX.EXTRA)
            # Spark heat in range 0.5 - 1
            f[pos] += random() * 0.5 + 0.5
            if f[pos] > 1.0:
                # Clamp pixel heat to maximum of 1
                f[pos] = 1.0
        # Convert heat to LED colors
        img = Image.new('RGBA', self.size)
        pix = img.load()
        for i in range(self.size[0]):
            p = self.palette(f[i + FlameFX.EXTRA])
            for j in range(self.size[1]):
                pix[i, j] = p
        return img
