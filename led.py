import spectra
from fakepixel import Fake_NeoPixel
try:
    from neopixel import Adafruit_NeoPixel, Color, ws
    realpixels = True
except ImportError:
    from fakepixel import Color, ws
    realpixels = False


def col(c, gamma=None):
    if not isinstance(c, tuple):
        c = spectra.html(c).color_object.get_upscaled_value_tuple()
    if gamma:
        c = tuple(int(((i / 255.0) ** gamma) * 255) for i in c)
    return Color(*c[:3])


class LEDStrip:
    STRIPS = {'rgb': ws.WS2811_STRIP_RGB,
              'rbg': ws.WS2811_STRIP_RBG,
              'grb': ws.WS2811_STRIP_GRB,
              'gbr': ws.WS2811_STRIP_GBR,
              'brg': ws.WS2811_STRIP_BRG,
              'bgr': ws.WS2811_STRIP_BGR,
              'rgbw': ws.SK6812_STRIP_RGBW}

    def __init__(self, kind, leds, freq, pin, dma, channel, strip, invert, bright, gamma, debug):
        # bg: solid, gradient, fade
        # fg: drop, flash, sparkle
        strip_type = self.STRIPS[strip]
        self._gamma = gamma
        if kind == 'real' or (kind == 'auto' and realpixels):
            if not realpixels:
                raise Exception("Can't load library for real pixels")
            self.leds = Adafruit_NeoPixel(leds, pin, freq, dma, invert,
                                          bright, channel, strip_type)
        else:
            self.leds = Fake_NeoPixel(leds, pin, freq, dma, invert,
                                      bright, channel, strip_type, debug)
        # Intialize the library (must be called once before other functions).
        self.leds.begin()

    def brightness(self, bright):
        self.leds.setBrightness(bright)
        self._display()

    def gamma(self, val):
        self._gamma = val
        self._display()

    def clear(self):
        self.solid('#000')

    def solid(self, colour):
        n = self.leds.numPixels()
        c = col(colour, self._gamma)
        self.leds.setPixelColor(slice(0, n), [c]*n)
        self._display()

    def gradient(self, colour1, colour2):
        n = self.leds.numPixels()
        pix = [col(c, self._gamma) for c in colour.Color(colour1).range_to(colour2, n)]
        self.leds.setPixelColor(slice(0, n), pix)
        self._display()

    def image(self, image):
        data = image.getdata()
        n = min(self.leds.numPixels(), len(data))
        pix = [col(c, self._gamma) for c in data]
        self.leds.setPixelColor(slice(0, n), pix)
        self._display()

    def _display(self):
        self.leds.show()
