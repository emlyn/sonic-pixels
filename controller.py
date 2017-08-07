from asyncio import get_event_loop
from fx import FXBase
from PIL import Image

import re


class Controller:
    FX_SUFFIX = re.compile('fx$')

    def __init__(self, width, height, period, leds, debug):
        self.period = period
        self.leds = leds
        self.size = (width, height)
        self.debug = debug
        self.layers = {}
        self.loop = get_event_loop()
        self.handle = self.loop.call_soon(self._loop, self.loop)
        self.last = None
        self.fx = {self._fx_addr(fx): fx
                   for fx in FXBase.__subclasses__()}

    def _fx_addr(self, fx):
        # FX name in lower case with 'fx' suffix removed, and '/' in front
        return '/' + re.sub(Controller.FX_SUFFIX, '', fx.__name__.lower(), 1)

    def handler(self, addr, *args):
        if self.debug:
            print(addr, args)
        if addr == '/bright':
            self.last = None
            self.leds.brightness(*args)
        elif addr == '/gamma':
            self.last = None
            self.leds.gamma(*args)
        elif addr in ('/clear', '/kill'):
            self.layers = {}
        elif addr == '/mod':
            prev = self.layers[100].image if 100 in self.layers else None
            self.layers[100] = [FadeFX(self.size, *args), prev]
        elif addr in self.fx:
            fxclass = self.fx[addr]
            fx = fxclass(self.size, args)
            layer = fx.default_layer()
            if layer in self.layers:
                fx.image = self.layers[layer].image
            self.layers[layer] = fx
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
