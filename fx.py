import colour
from PIL import Image, ImageChops, ImageColor
from bisect import bisect_right
from math import exp, sqrt
from numbers import Number
from random import choice, random, randrange


def gradient(size, colours, ring=False):
    img = Image.new('RGBA', size)
    pix = img.load()
    if len(colours) == 0:
        colours = ['black']
    if ring:
        colours.append(colours[0])
    scale = colour.scale(*colours)
    for x in range(size[0]):
        if size[0] < 2:
            i = 0.5
        else:
            i = x / (size[0] - 1.0)
        c = scale(i)
        for y in range(size[1]):
            pix[x, y] = c
    return img

class FXBase(object):
    def __init__(self, size, prev, args):
        self.size = size
        self.time = None
        self.start_time = None
        self.previous_time = None
        self.image = prev
        self.background = None
        self._params = self.params(args)

    def __getattr__(self, nm):
        if nm == '_params':
            raise Exception("Can't use params during initialisation")
        return self._params[nm]

    def params(self, args):
        return {}

    def render(self):
        raise NotImplementedError("FX implementations must implement render")

    def next_image(self, time, background):
        if self.start_time is None:
            self.start_time = time
        self.previous_time = self.time
        self.time = time
        self.background = background
        self.image = self.render()
        return self.image


class SolidFX(FXBase):
    def params(self, colours):
        return dict(_img=gradient(self.size, colours))

    def render(self):
        return self._img


class FadeFX(FXBase):
    def params(self, vals):
        imgs = []
        cols = []
        tlast = 0
        for v in vals:
            if isinstance(v, Number):
                if len(cols) == 0 and len(imgs) == 0:
                    img = None
                else:
                    img = gradient(self.size, cols)
                imgs.append([tlast, img])
                tlast += v
                cols = []
            else:
                cols.append(v)
        imgs.append([tlast, gradient(self.size, cols)])
        return dict(_imgs=imgs)

    def render(self):
        imgs = self._imgs
        if imgs[0][1] is None:
            imgs[0][1] = self.background
        if self.time <= self.start_time:
            return imgs[0][1]
        elif self.time >= self.start_time + imgs[-1][0]:
            return imgs[-1][1]
        i = bisect_right(imgs, [self.time - self.start_time, None])
        a = (self.time - self.start_time - imgs[i-1][0]) / (imgs[i][0] - imgs[i-1][0])
        print('dbg i={}, a={}, imgs={}'.format(i, a, imgs))
        return Image.blend(imgs[i-1][1], imgs[i][1], a)


class SpinFX(FXBase):
    def params(self, args):
        imgs = []
        period = args[0]
        cols = []
        tlast = 0
        for v in args[1:]:
            if isinstance(v, Number):
                if len(cols) == 0 and len(self.imgs) == 0:
                    img = None
                else:
                    img = gradient(self.size, cols, True)
                imgs.append([tlast, img])
                tlast += v
                cols = []
            else:
                cols.append(v)
        imgs.append([tlast, gradient(self.size, cols, True)])
        return dict(period=period, _imgs=imgs)

    def render(self):
        imgs = self._imgs
        if imgs[0][1] is None:
            imgs[0][1] = self.background
        if self.time <= self.start_time:
            return imgs[0][1]
        elif self.time >= self.start_time + imgs[-1][0]:
            return None
        i = bisect_right(imgs, [self.time - self.start_time, None])
        a = (self.time - self.start_time - imgs[i-1][0]) / (imgs[i][0] - imgs[i-1][0])
        img = Image.blend(imgs[i-1][1], imgs[i][1], a)
        shift = int(img.size[0] * (self.time - self.start_time) / self.period)
        return ImageChops.offset(img, shift, 0)


class SlideFX(FXBase):
    def params(self, args):
        period = 1
        if len(args) > 0 and isinstance(args[0], Number):
            period = args[0]
            args = args[1:]
        width = max(self.size[0] // 10, 4)
        if len(args) > 0 and isinstance(args[0], Number):
            width = args[0]
            args = args[1:]
        fade = int(sqrt(max(width, 0) / 1.5))
        if len(args) > 0 and isinstance(args[0], Number):
            fade = args[0]
            args = args[1:]
        sprite = gradient((width, self.size[1]), args if len(args) > 0 else ['white'])
        pix = sprite.load()
        for x in range(min(fade, (width + 1) // 2)):
            v = (x + 1) / (fade + 1)
            for y in range(self.size[1]):
                p = pix[x, y]
                pix[x, y] = p[0:3] + (int(p[3] * v),)
                if x < width // 2:
                    # Dont double-fade central pixel on odd widths
                    p = pix[width - 1 - x, y]
                    pix[width - 1 - x, y] = p[0:3] + (int(p[3] * v),)
        return dict(period=period, width=width, fade=fade, _sprite=sprite)

    def render(self):
        if self.time > self.start_time + abs(self.period):
            return None
        img = Image.new('RGBA', self.size, (0, 0, 0, 0))
        a = (self.time - self.start_time) / abs(self.period)
        if self.period < 0:
            a = 1 - a
        x = round(a * (self.size[0] + self.width) - self.width)
        img.paste(self._sprite, (x, 0))
        return img


class ChaseFX(FXBase):
    def params(self, args):
        period = 1
        if len(args) > 0 and isinstance(args[0], Number):
            period = args[0]
            args = args[1:]

        ratio = 0.05
        if len(args) > 0 and isinstance(args[0], Number):
            ratio = args[0]
            args = args[1:]

        reps = -1
        if len(args) > 0 and isinstance(args[0], Number):
            reps = args[0]
            args = args[1:]

        width = max(self.size[0] // 10, 4)
        if len(args) > 0 and isinstance(args[0], Number):
            width = args[0]
            args = args[1:]

        fade = int(sqrt(max(width, 0) / 1.5))
        if len(args) > 0 and isinstance(args[0], Number):
            fade = args[0]
            args = args[1:]

        sprite = gradient((width, self.size[1]), args if len(args) > 0 else ['white'])
        pix = sprite.load()
        for x in range(min(fade, (width + 1) // 2)):
            v = (x + 1) / (fade + 1)
            for y in range(self.size[1]):
                p = pix[x, y]
                pix[x, y] = p[0:3] + (int(p[3] * v),)
                if x < width // 2:
                    # Dont double-fade central pixel on odd widths
                    p = pix[width - 1 - x, y]
                    pix[width - 1 - x, y] = p[0:3] + (int(p[3] * v),)
        return dict(period=period, ratio=ratio, reps=reps, width=width, fade=fade, _sprite=sprite)

    def render(self):
        if self.reps >= 0 and (self.time > self.start_time + abs(self.period) * self.reps):
            return None
        img = Image.new('RGBA', self.size, (0, 0, 0, 0))
        t = self.time - self.start_time
        if self.period < 0:
            t -= self.period
        t %= abs(2 * self.period)
        d = 1
        if t > abs(self.period):
            t -= abs(self.period)
            d = -1
        a = min(1.0, t / abs(self.period * (1.0 - self.ratio)))
        if d < 0:
            a = 1.0 - a
        x = round(a * (self.size[0] - self.width))
        img.paste(self._sprite, (x, 0))
        return img


class FlashFX(FXBase):
    def params(self, args):
        period = 0
        if len(args) > 0 and isinstance(args[0], Number):
            period = args[0]
            args = args[1:]
        img = gradient(self.size, args)
        trans = Image.new('RGBA', self.size, (0, 0, 0, 0))
        return dict(period=period, _img=img, _trans=trans)

    def render(self):
        if self.time > self.start_time + self.period:
            return None
        if self.period <= 0:
            return self.img
        a = (self.time - self.start_time) / self.period
        return Image.blend(self._img, self._trans, a)


class SparkleFX(FXBase):
    def params(self, args):
        period = 0
        if len(args) > 0 and isinstance(args[0], Number):
            period = args[0]
            args = args[1:]
        fade = 0
        if len(args) > 0 and isinstance(args[0], Number):
            fade = args[0]
            args = args[1:]
        nspark = 10
        if len(args) > 0 and isinstance(args[0], Number):
            nspark = args[0]
            args = args[1:]
        colours = [ImageColor.getrgb(c) for c in (args if len(args) > 0 else ['white'])]
        img = Image.new('RGBA', self.size, (0, 0, 0, 0))
        trans = Image.new('RGBA', self.size, (0, 0, 0, 0))
        return dict(period=period, fade=fade, nspark=nspark, colours=colours, _img=img, _trans=trans)

    def render(self):
        if self.time > self.start_time + self.period + self.fade:
            return None
        pix = self._img.load()
        if self.previous_time is not None:
            nfade = 255 if self.fade <= 0 else round(255 * (self.time - self.previous_time) / self.fade)
            for y in range(self.size[1]):
                for x in range(self.size[0]):
                    p = pix[x, y]
                    pix[x, y] = p[:3] + (max(0, p[3] - nfade),)
        if self.time < self.start_time + self.period:
            for i in range(self.nspark):
                pix[randrange(self.size[0]), randrange(self.size[1])] = choice(self.colours)
        return self._img


class FlameFX(FXBase):
    EXTRA = 10 # Extra pixels before start of strip where sparks are generated
    # Adapted from https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/#fire
    def params(self, args):
        flame = [0.0] * (self.size[0] + FlameFX.EXTRA)
        sparking = args[0] if len(args) > 0 else 1 # Average number of sparks per frame
        cooling = args[1] if len(args) > 1 else 1 # Cooling rate
        kernel = self.parse_kernel(args[2]) if len(args) > 2 else [0, 1, 2] # Drift + diffusion
        palette = colour.scale('flame')
        return dict(_flame=flame, sparking=sparking, cooling=cooling, kernel=kernel, _palette=palette)

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

    def render(self):
        f = self._flame
        # Cool down every cell a little
        for i in range(len(f)):
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
            p = self._palette(f[i + FlameFX.EXTRA])
            for j in range(self.size[1]):
                pix[i, j] = p
        return img
