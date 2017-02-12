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
