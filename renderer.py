from abc import ABC


class Renderer(ABC):
    """Abstract base class for a Tinyland renderer."""

    def setup(self):
        pass

    def toggle_fullscreen(self):
        pass

    def show_calibration_markers(self):
        pass

    def render(self, ctx):
        pass
