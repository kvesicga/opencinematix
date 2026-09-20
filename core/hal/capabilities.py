from abc import ABC, abstractmethod


class DiscreteTrigger(ABC):
    """Fires an event. A push button."""

    @abstractmethod
    def on_trigger(self, callback):
        ...


class RelativeDelta(ABC):
    """Reports signed increments. A rotary encoder."""

    @abstractmethod
    def on_delta(self, callback):
        ...


class TextSurface(ABC):
    """Renders lines of text. A small display."""

    @abstractmethod
    def show(self, lines):
        ...
