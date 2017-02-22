import spectra
from PIL import Image


def gradient(size, colours):
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
        if len(colours) == 0:
            self.img = Image.new('RGBA', size, 'black')
        elif len(colours) == 1:
            self.img = Image.new('RGBA', size, colours[0])
        else:
            self.img = gradient(size, colours)

    def getDisplay(self, time, previous):
        return self.img


class FadeFX(FXBase):
    def __init__(self, size, time, colour):
        super().__init__(size)
        self.time = time
        self.colour = colour
        self.img = Image.new('RGBA', size, colour)
        self.start_t = None
        self.start_img = None

    def getDisplay(self, time, previous):
        if self.start_t is None:
            self.start_t = time
            if previous is None:
                self.start_img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            else:
                self.start_img = previous
        # print("fade", time, previous, self.start_t, self.time)
        if time >= self.start_t + self.time:
            return self.img
        a = (time - self.start_t) / self.time
        return Image.blend(self.start_img, self.img, a)
