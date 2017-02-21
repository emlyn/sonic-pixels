#!/usr/bin/env python3

import argparse
import asyncio
import signal

from osc import OSCServer
from led import LEDStrip
from controller import Controller


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port to listen on")
    parser.add_argument("--no-clear", action="store_false", dest="clear",
                        help="Don't clear LEDs on exit")
    parser.add_argument("--bright", type=int, default=255,
                        help="Initial brightness of LED strip (0-255)")
    parser.add_argument("--strip", default='grb',
                        choices=['rgb', 'rbg', 'grb', 'gbr',
                                 'brg', 'bgr', 'rgbw'])
    parser.add_argument("--kind", default="auto",
                        choices=["auto", "fake", "real"])
    parser.add_argument("--width", type=int, default=60,
                        help="Width of LED array")
    parser.add_argument("--height", type=int, default=1,
                        help="Height of LED array")
    parser.add_argument("--period", type=float, default=0.05,
                        help="Refresh period in seconds")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dma", type=int, default=5)
    parser.add_argument("--gpio", type=int, default=18,
                        choices=[12, 18, 40, 52])
    parser.add_argument("--channel", type=int, default=0, choices=[0, 1])
    parser.add_argument("--freq", type=int, default=800000)
    parser.add_argument("--invert", action="store_true")

    args = parser.parse_args()
    print("Args:", args)

    loop = asyncio.get_event_loop()
    leds = LEDStrip(args.kind, args.width * args.height, args.freq, args.gpio,
                    args.dma, args.channel, args.strip, args.invert,
                    args.bright, args.debug)
    controller = Controller(args.width, args.height, args.period, leds, args.debug)

    def cleanup():
        loop.stop()
        if args.clear:
            if args.debug:
                print()
            leds.clear()
        print("\nQuitting...")
    loop.add_signal_handler(signal.SIGINT, cleanup)
    loop.add_signal_handler(signal.SIGTERM, cleanup)
    print('Press Ctrl-C to quit')

    server = OSCServer(controller.handler, args.port, args.ip)

    try:
        loop.run_forever()
    finally:
        loop.close()
