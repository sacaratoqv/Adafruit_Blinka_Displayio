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
`displayio`
================================================================================

displayio for Blinka

**Software and Dependencies:**

* Adafruit Blinka:
  https://github.com/adafruit/Adafruit_Blinka/releases

* Author(s): Melissa LeBlanc-Williams

"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_Blinka_displayio.git"


class ColorConverter:
    """Converts one color format to another. Color converter based on original displayio
    code for consistency.
    """

    def __init__(self, *, dither=False):
        """Create a ColorConverter object to convert color formats.
        Only supports rgb888 to RGB565 currently.
        :param bool dither: Adds random noise to dither the output image
        """
        self._dither = dither
        self._depth = 16

    # pylint: disable=no-self-use
    def _compute_rgb565(self, color):
        self._depth = 16
        return (color >> 19) << 11 | ((color >> 10) & 0x3F) << 5 | (color >> 3) & 0x1F

    def _compute_luma(self, color):
        red = color >> 16
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        return (red * 19) / 255 + (green * 182) / 255 + (blue + 54) / 255

    def _compute_chroma(self, color):
        red = color >> 16
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        return max(red, green, blue) - min(red, green, blue)

    def _compute_hue(self, color):
        red = color >> 16
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        max_color = max(red, green, blue)
        chroma = self._compute_chroma(color)
        if chroma == 0:
            return 0
        hue = 0
        if max_color == red:
            hue = (((green - blue) * 40) / chroma) % 240
        elif max_color == green:
            hue = (((blue - red) + (2 * chroma)) * 40) / chroma
        elif max_color == blue:
            hue = (((red - green) + (4 * chroma)) * 40) / chroma
        if hue < 0:
            hue += 240

        return hue

    def _dither_noise_1(self, noise):
        noise = (noise >> 13) ^ noise
        more_noise = (
            noise * (noise * noise * 60493 + 19990303) + 1376312589
        ) & 0x7FFFFFFF
        return (more_noise / (1073741824.0 * 2)) * 255

    def _dither_noise_2(self, x, y):
        return self._dither_noise_1(x + y * 0xFFFF)

    def _compute_tricolor(self):
        pass

    def convert(self, color):
        "Converts the given rgb888 color to RGB565"
        if self._dither:
            return color  # To Do: return a dithered color
        return self._compute_rgb565(color)

    # pylint: enable=no-self-use

    @property
    def dither(self):
        """When true the color converter dithers the output by adding
        random noise when truncating to display bitdepth
        """
        return self._dither

    @dither.setter
    def dither(self, value):
        if not isinstance(value, bool):
            raise ValueError("Value should be boolean")
        self._dither = value
