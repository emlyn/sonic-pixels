from asyncio import get_event_loop
from PIL import Image
from fx import *


class Controller:
    def __init__(self, width, height, period, leds, debug):
        self.period = period
        self.leds = leds
        self.size = (width, height)
        self.debug = debug
        self.layers = {}
        self.loop = get_event_loop()
        self.handle = self.loop.call_soon(self._loop, self.loop)
        self.last = None

    def handler(self, addr, *args):
        if self.debug:
            print(addr, args)
        if addr == '/bright':
            self.last = None
            self.leds.brightness(*args)
        elif addr == '/gamma':
            self.last = None
            self.leds.gamma(*args)
        elif addr == '/clear':
            self.layers = {}
        elif addr == '/bg':
            prev = self.layers[10][1] if 10 in self.layers else None
            self.layers[10] = [SolidFX(self.size, *args), prev]
        elif addr == '/fade':
            prev = self.layers[20][1] if 20 in self.layers else None
            self.layers[20] = [FadeFX(self.size, *args), prev]
        elif addr == '/spin':
            prev = self.layers[30][1] if 30 in self.layers else None
            self.layers[30] = [SpinFX(self.size, *args), prev]
        elif addr == '/chase':
            prev = self.layers[40][1] if 40 in self.layers else None
            self.layers[40] = [ChaseFX(self.size, *args), prev]
        elif addr == '/slide':
            prev = self.layers[50][1] if 50 in self.layers else None
            self.layers[50] = [SlideFX(self.size, *args), prev]
        elif addr == '/flash':
            prev = self.layers[60][1] if 60 in self.layers else None
            self.layers[60] = [FlashFX(self.size, *args), prev]
        elif addr == '/sparkle':
            prev = self.layers[70][1] if 70 in self.layers else None
            self.layers[70] = [SparkleFX(self.size, *args), prev]
        elif addr == '/flame':
            prev = self.layers[80][1] if 80 in self.layers else None
            self.layers[80] = [FlameFX(self.size, *args), prev]
        elif addr == '/kill':
            self.layers = {}
        else:
            print("Unrecognised CMD:", addr, args)
        self.handle.cancel()
        self.handle = self.loop.call_soon(self._loop, self.loop)

    def update(self, time):
        img = Image.new('RGBA', self.size, (0, 0, 0, 255))
        for n in sorted(self.layers.keys()):
            layer, prev = self.layers[n]
            nextimg = layer.getDisplay(time, prev)
            self.layers[n][1] = nextimg
            if nextimg is not None:
                img = Image.alpha_composite(img, nextimg)
        if img != self.last:
            self.leds.image(img)
        self.last = img

    def _loop(self, loop, time=None):
        if time is None:
            time = loop.time()
        self.update(loop.time())
        self.handle = loop.call_at(time + self.period, self._loop,
                                   loop, time + self.period)
