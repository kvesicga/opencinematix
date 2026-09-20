from gpiozero import Button

from core.hal.capabilities import RelativeDelta
from core.hal.quadrature import QuadratureDecoder


class RotaryEncoder(RelativeDelta):
    def __init__(self, pin_a, pin_b):
        self.decoder = QuadratureDecoder()
        self.callback = None

        self.a = Button(pin_a, pull_up = True)
        self.b = Button(pin_b, pull_up = True)

        for pin in (self.a, self.b):
            pin.when_pressed = self._handle_edge
            pin.when_released = self._handle_edge

    def _handle_edge(self):
        step = self.decoder.update(self.a.value, self.b.value)

        if step and self.callback:
            self.callback(step)

    def on_delta(self, callback):
        self.callback = callback

    def close(self):
        for pin in (self.a, self.b):
            pin.when_pressed = None
            pin.when_released = None
            pin.close()
