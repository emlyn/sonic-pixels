from asyncio import get_event_loop
from PIL import Image
from fx import SolidFX


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
            self.leds.brightness(*args)
        elif addr == '/bg':
            print("BG", args)
            self.layers[10] = SolidFX(self.size, *args)
        else:
            print("Unrecognised CMD:", addr, args)

    def update(self, time):
        img = Image.new('RGBA', self.size, (0, 0, 0, 255))
        for n in sorted(self.layers.keys()):
            #print("Layer", n, self.layers[n])
            prev = None  # TODO
            img = Image.alpha_composite(img, self.layers[n].getDisplay(time, prev))
        self.leds.image(img)

    def _loop(self, loop, time=None):
        if time is None:
            time = loop.time()
        self.update(loop.time())
        self.handle = loop.call_at(time + self.period, self._loop, loop, time + self.period)
