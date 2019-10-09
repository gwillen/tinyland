from collections import namedtuple


# Convenience class that allows indexing as well as x and y attribute access
XYPoint = namedtuple("XYPoint", ["x", "y"])


class Shape:
    """Base class for shapes to draw on the landscape."""

    def __init__(self, x, y):
        self.center = XYPoint(x, y)


class Circle(Shape):

    def __init__(self, x, y, radius):
        super().__init__(x, y)
        self.radius = radius


class Rectangle(Shape):

    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height


class Text(Shape):

    def __init__(self, x, y, content):
        super().__init__(x, y)
        self.content = content


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

    def rect(self, x, y, width, height):
        self.shapes.append(Rectangle(x, y, width, height))

    def circle(self, x, y, radius):
        self.shapes.append(Circle(x, y, radius))

    def text(self, x, y, content):
        self.shapes.append(Text(x, y, content))

