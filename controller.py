from asyncio import get_event_loop
from PIL import Image
from fx import SolidFX, FadeFX, SpinFX, RotateFX, ChaseFX, SlideFX, FlashFX, SparkleFX, FlameFX


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
            prev = self.layers[10].image if 10 in self.layers else None
            self.layers[10] = SolidFX(self.size, prev, args)
        elif addr == '/fade':
            prev = self.layers[20].image if 20 in self.layers else None
            self.layers[20] = FadeFX(self.size, prev, args)
        elif addr == '/spin':
            prev = self.layers[30].image if 30 in self.layers else None
            self.layers[30] = SpinFX(self.size, prev, args)
        elif addr == '/rotate':
            prev = self.layers[40].image if 40 in self.layers else None
            self.layers[40] = RotateFX(self.size, prev, args)
        elif addr == '/chase':
            prev = self.layers[50].image if 50 in self.layers else None
            self.layers[50] = ChaseFX(self.size, prev, args)
        elif addr == '/slide':
            prev = self.layers[60].image if 60 in self.layers else None
            self.layers[60] = SlideFX(self.size, prev, args)
        elif addr == '/flash':
            prev = self.layers[70].image if 70 in self.layers else None
            self.layers[70] = FlashFX(self.size, prev, args)
        elif addr == '/sparkle':
            prev = self.layers[80].image if 80 in self.layers else None
            self.layers[80] = SparkleFX(self.size, prev, args)
        elif addr == '/flame':
            prev = self.layers[90].image if 90 in self.layers else None
            self.layers[80] = [FlameFX(self.size, *args), prev]
        elif addr == '/mod':
            prev = self.layers[100].image if 100 in self.layers else None
            self.layers[100] = [FadeFX(self.size, *args), prev]
        elif addr == '/kill':
            self.layers = {}
        else:
            print("Unrecognised CMD:", addr, args)
        self.handle.cancel()
        self.handle = self.loop.call_soon(self._loop, self.loop)

    def update(self, time):
        img = Image.new('RGBA', self.size, (0, 0, 0, 255))
        for n in sorted(self.layers.keys()):
            layer = self.layers[n]
            nextimg = layer.next_image(time, img)
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
