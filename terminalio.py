# The MIT License (MIT)
#
# Copyright (c) 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`terminalio`
================================================================================

terminalio for Blinka

**Software and Dependencies:**

* Adafruit Blinka:
  https://github.com/adafruit/Adafruit_Blinka/releases

* Author(s): Melissa LeBlanc-Williams

"""

import sys  # pylint: disable=unused-import
import fontio
from displayio.tilegrid import TileGrid

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_Blinka_displayio.git"

FONT = fontio.BuiltinFont()

# TODO: Tap into stdout to get the REPL
# sys.stdout = open('out.dat', 'w')
# sys.stdout.close()


class Terminal:
    """Displays text in a TileGrid

    The terminalio module contains classes to display a character stream on a display. The built in font is available as terminalio.FONT.
    """

    def __init__(self, tilegrid, font):
        if not isinstance(tilefrid, TileGrid):
            raise TypeError("Expected a TileGrid")
        self._tilegrid = tilegrid
        if not isinstance(font, fontio.BuiltinFont):
            raise TypeError("Expected a BuiltinFont")
        self._font = font
        self._cursor_x = 0
        self._curcor_y = 0
        self._first_row = 0
        for x in range(self._tilegrid.width):
            for y in range(self._tilegrid.height):
                self._tilegrid[x, y] = 0

    def write(self, buf):
        """Write the buffer of bytes to the bus."""
        pass
