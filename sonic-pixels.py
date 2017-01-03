#!/usr/bin/env python3

import argparse
import asyncio
import signal

from server import OSCServer
from controller import LEDController


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port to listen on")
    parser.add_argument("--clear", action="store_true")
    parser.add_argument("--bright", type=int, default=255)
    parser.add_argument("--strip", default='brg',
                        choices=['rgb', 'rbg', 'grb', 'gbr',
                                 'brg', 'bgr', 'rgbw'])
    parser.add_argument("--count", type=int, default=60)
    parser.add_argument("--dma", type=int, default=5)
    parser.add_argument("--gpio", type=int, default=18,
                        choices=[12, 18, 40, 52])
    parser.add_argument("--channel", type=int, default=0, choices=[0, 1])
    parser.add_argument("--freq", type=int, default=800000)
    parser.add_argument("--invert", action="store_true")

    args = parser.parse_args()
    print("Args:", args)

    loop = asyncio.get_event_loop()

    for signame in ('SIGINT', 'SIGTERM'):
        def ask_exit():
            print("\nStopping (%s)" % signame)
            loop.stop()
        loop.add_signal_handler(getattr(signal, signame), ask_exit)
    print('Press Ctrl-C to exit')

    leds = LEDController(args.count, args.freq, args.gpio, args.dma,
                         args.channel, args.strip, args.invert, args.bright)

    handlers = {'clear': lambda addr, args: leds.clear(),
                'bright': lambda addr, args: leds.bright(args[0]),
                'bg': lambda addr, args: leds.solid(args[0])}
    server = OSCServer(handlers, args.port, args.ip)

    loop.call_later(2, lambda ld: ld.gradient('#888', '#222'), leds)
    try:
        loop.run_forever()
    finally:
        loop.close()
