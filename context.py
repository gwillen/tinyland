from collections import namedtuple


# Convenience class that allows indexing as well as x and y attribute access
XYPoint = namedtuple("XYPoint", ["x", "y"])


# BGR color values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
YELLOW = (0, 255, 255)


class Shape:
    """Base class for shapes to draw on the landscape."""

    def __init__(self, x, y, color):
        self.center = XYPoint(x, y)
        self.color = color


class Circle(Shape):

    def __init__(self, x, y, radius, color):
        super().__init__(x, y, color)
        self.radius = radius


class Rectangle(Shape):

    def __init__(self, x, y, width, height, rotation, color):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
        self.rotation = rotation


class Text(Shape):

    def __init__(self, x, y, content, color, size):
        super().__init__(x, y, color)
        self.content = str(content)
        self.size = size


class Image(Shape):
    def __init__(self, filepath, x, y, width, height):
        super().__init__(x, y, color=BLACK)
        self.width = width
        self.height = height
        self.filepath = filepath


class DrawingContext:
    """Context with all information to project a drawing onto the landscape.

    Args:
        width (int): width of the drawing
        height (int): height of the drawing
    Attributes:
        width (int): width of the drawing
        height (int): height of the drawing
        shapes (list<Shape>): shapes to draw
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.shapes = []

    def rect(self, x, y, width, height, rotation=0, color=WHITE):
        self.shapes.append(Rectangle(x, y, width, height, rotation, color))

    def circle(self, x, y, radius, color=WHITE):
        self.shapes.append(Circle(x, y, radius, color))

    def text(self, x, y, content, color=WHITE, size=2):
        self.shapes.append(Text(x, y, content, color, size))

    def image(self, filepath, x, y, width, height):
        self.shapes.append(Image(filepath, x, y, width, height))

