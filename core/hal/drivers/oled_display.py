from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

from core.hal.capabilities import TextSurface


LINE_HEIGHT = 12


class OledDisplay(TextSurface):
    def __init__(self, address = 0x3c, port = 1, line_height = LINE_HEIGHT):
        self.device = sh1106(i2c(port = port, address = address))
        self.line_height = line_height

    @property
    def capacity(self):
        return self.device.height // self.line_height

    def show(self, lines):
        with canvas(self.device) as draw:
            for index, line in enumerate(lines[:self.capacity]):
                draw.text((0, index * self.line_height), str(line), fill = "white")

    def clear(self):
        self.device.clear()

    def close(self):
        self.device.cleanup()
