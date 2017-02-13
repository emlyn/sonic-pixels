# Sonic-Pixels

Interactive lighting effects for Sonic Pi.

Requires:
- A strip of NeoPixel LEDs (or similar, as long as it's supported by [rpi_ws281x](https://github.com/jgarff/rpi_ws281x)). If you don't have them yet, but still want to try this out, you can run in fake mode and it will just display the LED colours in the terminal.
- One Raspberry Pi, to control the LED strip (again, not needed to run in fake mode).
- One copy of [Sonic Pi](http://sonic-pi.net/), to make some phat beats and control your lighting fx.

It should work with any version of the Raspberry Pi, but I used a Pi zero set up to run in USB [OTG mode](https://gist.github.com/gbaman/975e2db164b3ca2b51ae11e45e8fd40a) (so it behaves like a USB gadget and draws its power from the host computer running Sonic Pi, and you also get a nice stable network connection over USB). Alternatively you could run Sonic Pi on the same Raspberry Pi that's controlling the LEDs, so you don't need a separate computer.
