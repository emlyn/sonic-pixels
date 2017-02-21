import sys

def Color(red, green, blue, white=0):
    return (white << 24) | (red << 16) | (green << 8) | blue


class ws:
    WS2811_STRIP_RGB = 1
    WS2811_STRIP_RBG = 2
    WS2811_STRIP_GRB = 3
    WS2811_STRIP_GBR = 4
    WS2811_STRIP_BRG = 5
    WS2811_STRIP_BGR = 6
    SK6812_STRIP_RGBW = 10


class Fake_NeoPixel:
    def __init__(self, num, pin, freq_hz=800000, dma=5, invert=False,
                 brightness=255, *args):
        self._ledstr = '●'  # small
        # self._ledstr = '⬤ '  # big
        self._led_data = [0]*num
        self._brightness = brightness

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        # Ensure default colour, and show cursor again
        print('\x1b[39;49m\x1b[?25h', file=sys.stderr)

    def begin(self):
        pass

    def show(self):
        b = self._brightness / 255.0

        def col(bits, shift):
            w = ((bits >> 24) & 0xff)
            c = ((bits >> shift) & 0xff)
            return min(255, round((c + w) * b))

        print('\x1b[?25l',  # Hide cursor
              '\x0d',       # Go back to start of line
              '\x1b[48;2;64;64;64m',  # Set grey background
              ''.join('\x1b[38;2;{r};{g};{b}m{s}'.format(r=col(c, 16),
                                                         g=col(c, 8),
                                                         b=col(c, 0),
                                                         s=self._ledstr)
                      for c in self._led_data),  # Coloured pixels
              '\x1b[39;49m',  # Reset colour to default
              '  ',           # Overwrite any following chars if present
              sep='', end='', file=sys.stderr)

    def setPixelColor(self, i, c):
        self._led_data[i] = c

    def setPixelColorRGB(self, i, r, g, b, w=0):
        self._led_data[i] = Color(r, g, b, w)

    def setBrightness(self, b):
        self._brightness = b

    def getPixels(self):
        return self._led_data

    def numPixels(self):
        return len(self._led_data)

    def getPixelColor(self, n):
        return self._led_data[n]
