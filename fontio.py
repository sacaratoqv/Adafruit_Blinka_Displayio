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
`fontio`
================================================================================

fontio for Blinka

**Software and Dependencies:**

* Adafruit Blinka:
  https://github.com/adafruit/Adafruit_Blinka/releases

* Author(s): Melissa LeBlanc-Williams

"""

from displayio import Bitmap
from PIL import ImageFont

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_Blinka_displayio.git"


class BuiltinFont:
    def __init__(self):
        self._font = ImageFont.load_default()
        ascii = ""
        for character in range(0x20, 0x7F):
            ascii += chr(character)
        self._font.getmask(ascii)
        bmp_size = self._font.getsize(ascii)
        self._bitmap = Bitmap(bmp_size[0], bmp_size[1], 2)
        ascii_mask = self._font.getmask(ascii, mode="1")
        for x in range(bmp_size[0]):
            for y in range(bmp_size[1]):
                self._bitmap[x, y] = 1 if ascii_mask.getpixel((x, y)) else 0

    def _get_glyph_index(self, charcode):
        if 0x20 <= charcode <= 0x7E:
            return charcode - 0x20

    def get_bounding_box(self):
        """Returns the maximum bounds of all glyphs in the font in a tuple of two values: width, height."""
        return self._font.getsize("M")

    def get_glyph(self, codepoint):
        """Returns a `fontio.Glyph` for the given codepoint or None if no glyph is available."""
        bounding_box = self._font.getsize(chr(codepoint))
        return Glyph(
            bitmap=self._bitmap,
            tile_index=self._get_glyph_index(codepoint),
            width=bounding_box[0],
            height=bounding_box[1],
            dx=0,
            dy=0,
            shift_x=0,
            shift_y=0,
        )

    @property
    def bitmap(self):
        """Bitmap containing all font glyphs starting with ASCII and followed by unicode. Use `get_glyph` in most cases. This is useful for use with `displayio.TileGrid` and `terminalio.Terminal`.
        """
        return self._bitmap


class Glyph:
    def __init__(self, *, bitmap, tile_index, width, height, dx, dy, shift_x, shift_y):
        self.bitmap = bitmap
        self.width = width
        self.height = height
        self.dx = dx
        self.dy = dy
        self.shift_x = shift_x
        self.shift_y = shift_y
        self.tile_index = tile_index
