import renderer
import context


class Renderer(renderer.Renderer):

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def setup(self):
        print('Running debug renderer.')

    def toggle_fullscreen(self):
        pass

    def show_calibration_markers(self):
        pass

    def render(self, ctx):
        """Display the draw context as text.

        Useful (perhaps?) as a debugging tool.

        Args:
          ctx (context.DrawingContext): A context with shapes to draw
        """
        for shape in ctx.shapes:
            if isinstance(shape, context.Rectangle):
                print("Rectangle at x: {} y: {}".format(shape.center.x, shape.center.y))
            elif isinstance(shape, context.Circle):
                print("Circle at x: {} y: {}".format(shape.center.x, shape.center.y))
            elif isinstance(shape, context.Text):
                print("Text at x: {} y: {} content: {}".format(shape.center.x, shape.center.y, shape.content))
            elif isinstance(shape, context.Image):
                print("Image at x: {} y: {} content: {}".format(shape.center.x, shape.center.y, shape.filepath))
            
            