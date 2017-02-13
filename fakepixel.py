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

class Fake_NeoPixel:
    def __init__(self, leds, *args):
        #self.ledstr = '●' # small
        self.ledstr = '⬤ ' # big
        self.leds = [0]*leds

    def numPixels(self):
        return len(self.leds)

    def begin(self):
        pass

    def setBrightness(self, b):
        pass

    def setPixelColor(self, i, c):
        self.leds[i] = c

    def setPixelColorRGB(self, i, r, g, b):
        self.leds[i] = Color(r, g, b)

    def show(self):
        print('\x0d',
              ''.join('\x1b[38;2;{r};{g};{b}m{s}'.format(r=(c >> 16) % 256,
                                                         g=(c >> 8) % 256,
                                                         b=c % 256,
                                                         s=self.ledstr)
                      for c in self.leds),
              '\x1b[39;49m',
              sep='', end='')
