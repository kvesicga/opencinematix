from gpiozero import Button

from core.hal.capabilities import DiscreteTrigger


class PushButton(DiscreteTrigger):
    def __init__(self, pin):
        self.p = Button(pin, pull_up = True, bounce_time = 0.05)
        self.callback = None

        self.p.when_pressed = self._handle_edge

    def _handle_edge(self):
        if self.callback:
            self.callback()

    def on_trigger(self, callback):
        self.callback = callback

    def close(self):
        self.p.when_pressed = None
        self.p.when_released = None
        self.p.close()
