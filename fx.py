import spectra
from PIL import Image
from bisect import bisect_right
from numbers import Number


def gradient(size, colours):
    if len(colours) < 2:
        return Image.new('RGBA', size, colours[0] if len(colours) > 0 else 'black')
    img = Image.new('RGBA', size)
    pix = img.load()
    scale = spectra.scale(colours)
    for x in range(size[0]):
        c = scale(x / (size[0] - 1.0))
        for y in range(size[1]):
            pix[x, y] = c.color_object.get_upscaled_value_tuple()
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
    def __init__(self, size, time, width, fade, *colours):
        self.start_t = None
        self.size = size
        self.width = width
        self.time = time
        self.sprite = gradient((width, size[1]), colours if len(colours) > 0 else ['white'])
        # TODO: fade edges (or better render in getDisplay with antialiasing)

    def getDisplay(self, time, previous):
        if self.start_t is None:
            self.start_t = time
        if time > self.start_t + self.time:
            return None
        img = Image.new('RGBA', self.size, (0, 0, 0, 0))
        a = (time - self.start_t) / self.time
        x = round(a * (self.size[0] + self.width) - self.width)
        img.paste(self.sprite, (x, 0))
        return img
