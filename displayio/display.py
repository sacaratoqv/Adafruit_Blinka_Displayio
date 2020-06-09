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
`displayio.display`
================================================================================

displayio for Blinka

**Software and Dependencies:**

* Adafruit Blinka:
  https://github.com/adafruit/Adafruit_Blinka/releases

* Author(s): Melissa LeBlanc-Williams

"""

import time
import struct
import threading
from PIL import Image
import numpy
from recordclass import recordclass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_Blinka_displayio.git"

Rectangle = recordclass("Rectangle", "x1 y1 x2 y2")
displays = []

# pylint: disable=unnecessary-pass, unused-argument

# pylint: disable=too-many-instance-attributes
class Display:
    """This initializes a display and connects it into CircuitPython. Unlike other objects
    in CircuitPython, Display objects live until ``displayio.release_displays()`` is called.
    This is done so that CircuitPython can use the display itself.

    Most people should not use this class directly. Use a specific display driver instead
    that will contain the initialization sequence at minimum.

    .. class::
        Display(display_bus, init_sequence, *, width, height, colstart=0, rowstart=0, rotation=0,
        color_depth=16, grayscale=False, pixels_in_byte_share_row=True, bytes_per_cell=1,
        reverse_pixels_in_byte=False, set_column_command=0x2a, set_row_command=0x2b,
        write_ram_command=0x2c, set_vertical_scroll=0, backlight_pin=None, brightness_command=None,
        brightness=1.0, auto_brightness=False, single_byte_bounds=False, data_as_commands=False,
        auto_refresh=True, native_frames_per_second=60)
    """

    # pylint: disable=too-many-locals
    def __init__(
        self,
        display_bus,
        init_sequence,
        *,
        width,
        height,
        colstart=0,
        rowstart=0,
        rotation=0,
        color_depth=16,
        grayscale=False,
        pixels_in_byte_share_row=True,
        bytes_per_cell=1,
        reverse_pixels_in_byte=False,
        set_column_command=0x2A,
        set_row_command=0x2B,
        write_ram_command=0x2C,
        set_vertical_scroll=0,
        backlight_pin=None,
        brightness_command=None,
        brightness=1.0,
        auto_brightness=False,
        single_byte_bounds=False,
        data_as_commands=False,
        auto_refresh=True,
        native_frames_per_second=60
    ):
        """Create a Display object on the given display bus (`displayio.FourWire` or
        `displayio.ParallelBus`).

        The ``init_sequence`` is bitpacked to minimize the ram impact. Every command begins
        with a command byte followed by a byte to determine the parameter count and if a
        delay is need after. When the top bit of the second byte is 1, the next byte will be
        the delay time in milliseconds. The remaining 7 bits are the parameter count
        excluding any delay byte. The third through final bytes are the remaining command
        parameters. The next byte will begin a new command definition. Here is a portion of
        ILI9341 init code:
        .. code-block:: python

            init_sequence = (
                b"\xe1\x0f\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F"
                b"\x11\x80\x78"# Exit Sleep then delay 0x78 (120ms)
                b"\x29\x80\x78"# Display on then delay 0x78 (120ms)
            )
            display = displayio.Display(display_bus, init_sequence, width=320, height=240)

        The first command is 0xe1 with 15 (0xf) parameters following. The second and third
        are 0x11 and 0x29 respectively with delays (0x80) of 120ms (0x78) and no parameters.
        Multiple byte literals (b”“) are merged together on load. The parens are needed to
        allow byte literals on subsequent lines.

        The initialization sequence should always leave the display memory access inline with
        the scan of the display to minimize tearing artifacts.
        """
        self._bus = display_bus
        self._set_column_command = set_column_command
        self._set_row_command = set_row_command
        self._write_ram_command = write_ram_command
        self._brightness_command = brightness_command
        self._data_as_commands = data_as_commands
        self._single_byte_bounds = single_byte_bounds
        self._width = width
        self._height = height
        self._colstart = colstart
        self._rowstart = rowstart
        self._rotation = rotation
        self._auto_brightness = auto_brightness
        self._brightness = brightness
        self._auto_refresh = auto_refresh
        self._initialize(init_sequence)
        self._buffer = Image.new("RGB", (width, height))
        self._subrectangles = []
        self._bounds_encoding = ">BB" if single_byte_bounds else ">HH"
        self._current_group = None
        displays.append(self)
        self._refresh_thread = None
        if self._auto_refresh:
            self.auto_refresh = True

    # pylint: enable=too-many-locals

    def _initialize(self, init_sequence):
        i = 0
        while i < len(init_sequence):
            command = init_sequence[i]
            data_size = init_sequence[i + 1]
            delay = (data_size & 0x80) > 0
            data_size &= ~0x80
            self._write(command, init_sequence[i + 2 : i + 2 + data_size])
            delay_time_ms = 10
            if delay:
                data_size += 1
                delay_time_ms = init_sequence[i + 1 + data_size]
                if delay_time_ms == 255:
                    delay_time_ms = 500
            time.sleep(delay_time_ms / 1000)
            i += 2 + data_size

    def _write(self, command, data):
        if self._single_byte_bounds:
            self._bus.send(True, bytes([command]) + data, toggle_every_byte=True)
        else:
            self._bus.send(True, bytes([command]), toggle_every_byte=True)
            self._bus.send(False, data)

    def _release(self):
        self._bus.release()
        self._bus = None

    def show(self, group):
        """Switches to displaying the given group of layers. When group is None, the
        default CircuitPython terminal will be shown.
        """
        self._current_group = group

    def refresh(self, *, target_frames_per_second=60, minimum_frames_per_second=1):
        """When auto refresh is off, waits for the target frame rate and then refreshes the
        display, returning True. If the call has taken too long since the last refresh call
        for the given target frame rate, then the refresh returns False immediately without
        updating the screen to hopefully help getting caught up.

        If the time since the last successful refresh is below the minimum frame rate, then
        an exception will be raised. Set minimum_frames_per_second to 0 to disable.

        When auto refresh is on, updates the display immediately. (The display will also
        update without calls to this.)
        """
        # Go through groups and and add each to buffer
        if self._current_group is not None:
            buffer = Image.new("RGBA", (self._width, self._height))
            # Recursively have everything draw to the image
            self._current_group._fill_area(buffer)  # pylint: disable=protected-access
            # save image to buffer (or probably refresh buffer so we can compare)
            self._buffer.paste(buffer)

        # Eventually calculate dirty rectangles here
        self._subrectangles.append(Rectangle(0, 0, self._width, self._height))

        for area in self._subrectangles:
            self._refresh_display_area(area)

    def _refresh_loop(self):
        while self._auto_refresh:
            self.refresh()

    def _refresh_display_area(self, rectangle):
        """Loop through dirty rectangles and redraw that area."""
        data = numpy.array(self._buffer.crop(rectangle).convert("RGB")).astype("uint16")
        color = (
            ((data[:, :, 0] & 0xF8) << 8)
            | ((data[:, :, 1] & 0xFC) << 3)
            | (data[:, :, 2] >> 3)
        )

        pixels = list(
            numpy.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()
        )

        self._write(
            self._set_column_command,
            self._encode_pos(
                rectangle.x1 + self._colstart, rectangle.x2 + self._colstart - 1
            ),
        )
        self._write(
            self._set_row_command,
            self._encode_pos(
                rectangle.y1 + self._rowstart, rectangle.y2 + self._rowstart - 1
            ),
        )
        self._write(self._write_ram_command, pixels)

    def _encode_pos(self, x, y):
        """Encode a postion into bytes."""
        return struct.pack(self._bounds_encoding, x, y)

    def fill_row(self, y, buffer):
        """Extract the pixels from a single row"""
        pass

    @property
    def auto_refresh(self):
        """True when the display is refreshed automatically."""
        return self._auto_refresh

    @auto_refresh.setter
    def auto_refresh(self, value):
        self._auto_refresh = value
        if self._refresh_thread is None:
            self._refresh_thread = threading.Thread(
                target=self._refresh_loop, daemon=True
            )
        if value and not self._refresh_thread.is_alive():
            # Start the thread
            self._refresh_thread.start()
        elif not value and self._refresh_thread.is_alive():
            # Stop the thread
            self._refresh_thread.join()

    @property
    def brightness(self):
        """The brightness of the display as a float. 0.0 is off and 1.0 is full `brightness`.
        When `auto_brightness` is True, the value of `brightness` will change automatically.
        If `brightness` is set, `auto_brightness` will be disabled and will be set to False.
        """
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value

    @property
    def auto_brightness(self):
        """True when the display brightness is adjusted automatically, based on an ambient
        light sensor or other method. Note that some displays may have this set to True by
        default, but not actually implement automatic brightness adjustment.
        `auto_brightness` is set to False if `brightness` is set manually.
        """
        return self._auto_brightness

    @auto_brightness.setter
    def auto_brightness(self, value):
        self._auto_brightness = value

    @property
    def width(self):
        """Display Width"""
        return self._width

    @property
    def height(self):
        """Display Height"""
        return self._height

    @property
    def rotation(self):
        """The rotation of the display as an int in degrees."""
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if value not in (0, 90, 180, 270):
            raise ValueError("Rotation must be 0/90/180/270")
        self._rotation = value

    @property
    def bus(self):
        """Current Display Bus"""
        return self._bus


# pylint: enable=too-many-instance-attributes
