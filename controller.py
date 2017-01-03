from asyncio import get_event_loop
import colour
try:
    from neopixel import Adafruit_NeoPixel, Color, ws
except ImportError:
    def Color(red, green, blue, white = 0):
        return (white << 24) | (red << 16)| (green << 8) | blue

    class ws:
        WS2811_STRIP_RGB = 1
        WS2811_STRIP_RBG = 2
        WS2811_STRIP_GRB = 3
        WS2811_STRIP_GBR = 4
        WS2811_STRIP_BRG = 5
        WS2811_STRIP_BGR = 6
        SK6812_STRIP_RGBW = 10

    class Adafruit_NeoPixel:
        def __init__(self, leds, *args):
            self.leds = leds

        def numPixels(self):
            return self.leds

        def begin(self):
            pass

        def setBrightness(self, b):
            pass

        def setPixelColor(self, *args):
            print('set', args)
            pass

        def setPixelColorRGB(self, *args):
            print('set', args)
            pass

        def show(self):
            pass


def col(c):
    col = colour.Color(c)
    return Color(int(col.red * 255), int(col.green*255), int(col.blue*255))


class LEDController:
    STRIPS = {'rgb': ws.WS2811_STRIP_RGB,
              'rbg': ws.WS2811_STRIP_RBG,
              'grb': ws.WS2811_STRIP_GRB,
              'gbr': ws.WS2811_STRIP_GBR,
              'brg': ws.WS2811_STRIP_BRG,
              'bgr': ws.WS2811_STRIP_BGR,
              'rgbw': ws.SK6812_STRIP_RGBW}

    def __init__(self, leds, freq, pin, dma, channel, strip, invert, bright, period=0.5):
        # bg: solid, gradient, fade
        # fg: drop, flash, sparkle
        strip_type = self.STRIPS[strip]
        self.leds = Adafruit_NeoPixel(leds, pin, freq, dma, invert,
                                      bright, channel, strip_type)
        # Intialize the library (must be called once before other functions).
        self.leds.begin()
        #self.running = False
        self.period = period

        loop = get_event_loop()
        loop.call_soon(self._loop, loop)

    def brightness(self, bright):
        self.leds.setBrightness(bright)
        #self.leds.show()

    def clear(self):
        self.solid('#000')

    def solid(self, colour):
        n = self.leds.numPixels()
        c = col(colour)
        self.leds.setPixelColor(slice(0, n), [c]*n)
        #self.leds.show()

    def gradient(self, colour1, colour2):
        n = self.leds.numPixels()
        pix = [col(c) for c in colour.Color(colour1).range_to(colour2, n)]
        self.leds.setPixelColor(slice(0, n), pix)
        #self.leds.show()

    def _display(self):
        self.leds.show()

    def _loop(self, loop, time = None):
        if time is None:
            time = loop.time()
        print('Loop: %s' % time)
        self._display()
        delay = time + self.period - loop.time()
        loop.call_later(max(delay, 0), self._loop, loop, time + self.period)
