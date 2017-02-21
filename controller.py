from asyncio import get_event_loop
from PIL import Image
from fx import SolidFX, FadeFX


class Controller:
    def __init__(self, width, height, leds):
        self.period = 0.1
        self.leds = leds
        self.size = (width, height)
        self.layers = {}
        loop = get_event_loop()
        self.handle = loop.call_soon(self._loop, loop)

    def handler(self, addr, *args):
        if addr == '/bright':
            # print("Brightness", args)
            self.leds.brightness(*args)
        elif addr == '/bg':
            # print("BG", args)
            prev = self.layers[10][1] if 10 in self.layers else None
            self.layers[10] = [SolidFX(self.size, *args), prev]
        elif addr == '/fade':
            # print("Fade", args)
            prev = self.layers[10][1] if 10 in self.layers else None
            self.layers[10] = [FadeFX(self.size, *args), prev]
        else:
            print("Unrecognised CMD:", addr, args)

    def update(self, time):
        img = Image.new('RGBA', self.size, (0, 0, 0, 255))
        for n in sorted(self.layers.keys()):
            layer, prev = self.layers[n]
            nextimg = layer.getDisplay(time, prev)
            self.layers[n][1] = nextimg
            img = Image.alpha_composite(img, nextimg)
        self.leds.image(img)

    def _loop(self, loop, time=None):
        if time is None:
            time = loop.time()
        self.update(loop.time())
        self.handle = loop.call_at(time + self.period, self._loop,
                                   loop, time + self.period)
