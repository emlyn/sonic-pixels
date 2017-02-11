#!/usr/bin/env python3

import argparse
import asyncio
import signal

from osc import OSCServer
from led import LEDController


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port to listen on")
    parser.add_argument("--no-clear", action="store_false", dest="clear",
                        help="Don't clear LEDs on exit")
    parser.add_argument("--bright", type=int, default=255)
    parser.add_argument("--strip", default='grb',
                        choices=['rgb', 'rbg', 'grb', 'gbr',
                                 'brg', 'bgr', 'rgbw'])
    parser.add_argument("--count", type=int, default=60,
                        help="Number of LEDs in the strip")
    parser.add_argument("--dma", type=int, default=5)
    parser.add_argument("--gpio", type=int, default=18,
                        choices=[12, 18, 40, 52])
    parser.add_argument("--channel", type=int, default=0, choices=[0, 1])
    parser.add_argument("--freq", type=int, default=800000)
    parser.add_argument("--invert", action="store_true")

    args = parser.parse_args()
    print("Args:", args)

    loop = asyncio.get_event_loop()
    leds = LEDController(args.count, args.freq, args.gpio, args.dma,
                         args.channel, args.strip, args.invert, args.bright)

    def cleanup():
        print("\nQuitting...")
        loop.stop()
        if args.clear:
            leds.clear()
            leds._display()
    loop.add_signal_handler(signal.SIGINT, cleanup)
    loop.add_signal_handler(signal.SIGTERM, cleanup)
    print('Press Ctrl-C to exit')

    def debug(*args):
        print("Got %d args: %s" % (len(args), str(args)))
    handlers = {'debug': debug,
                'clear': lambda addr, *args: leds.clear(),
                'bright': lambda addr, *args: leds.brightness(*args),
                'bg': lambda addr, *args: leds.solid(*args)}
    server = OSCServer(handlers, args.port, args.ip)

    try:
        loop.run_forever()
    finally:
        loop.close()
