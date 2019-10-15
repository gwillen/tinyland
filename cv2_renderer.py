import cv2
import numpy as np

import context
import renderer


class Renderer(renderer.Renderer):
    WINDOW_TITLE = "Tinyland"

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def setup(self):
        """Create the OpenCV window to display images to."""
        cv2.namedWindow(Renderer.WINDOW_TITLE)
        # Allow window to be fullsized by both the OS window controls and OpenCV
        cv2.setWindowProperty(Renderer.WINDOW_TITLE,
                              cv2.WND_PROP_AUTOSIZE,
                              cv2.WINDOW_NORMAL)

    def toggle_fullscreen(self):
        cur = cv2.getWindowProperty(Renderer.WINDOW_TITLE,
                                    cv2.WND_PROP_FULLSCREEN)
        if cur == cv2.WINDOW_NORMAL:
            cv2.setWindowProperty(Renderer.WINDOW_TITLE,
                                  cv2.WND_PROP_FULLSCREEN,
                                  cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(Renderer.WINDOW_TITLE,
                                  cv2.WND_PROP_FULLSCREEN,
                                  cv2.WINDOW_NORMAL)

    def show_calibration_markers(self):
        image = np.zeros((self.height, self.width, 3), np.uint8)

        # Display calibration markers until we find them
        M_SZ = 40
        marker = np.zeros((M_SZ, M_SZ, 3), dtype=np.uint8)
        cv2.rectangle(marker, (0, 0), (M_SZ, M_SZ), (255, 255, 255), cv2.FILLED)
        cv2.rectangle(marker, (10, 10), (M_SZ - 10, M_SZ - 10), (0, 0, 0),
                      cv2.FILLED)

        image[0:M_SZ, 0:M_SZ] = marker
        marker = cv2.rotate(marker, cv2.ROTATE_90_CLOCKWISE)
        image[0:M_SZ, self.width - M_SZ:self.width] = marker
        marker = cv2.rotate(marker, cv2.ROTATE_90_CLOCKWISE)
        image[self.height - M_SZ:self.height,
        self.width - M_SZ:self.width] = marker
        marker = cv2.rotate(marker, cv2.ROTATE_90_CLOCKWISE)
        image[self.height - M_SZ:self.height, 0:M_SZ] = marker

        self._display_frame(image)

    def render(self, ctx):
        """Display the draw context to the OpenCV window.

        Process all shapes in the context and render resulting image.

        Args:
          ctx (context.DrawingContext): A context with shapes to draw
        """
        image = np.zeros((self.height, self.width, 3), np.uint8)
        for shape in ctx.shapes:
            if isinstance(shape, context.Rectangle):
                x = int(shape.width / 2)
                y = int(shape.height / 2)
                rad = np.radians(shape.rotation)
                rotation = np.array([[np.cos(rad), -np.sin(rad)],
                                     [np.sin(rad), np.cos(rad)]])
                translation = np.array([[shape.center.x], [shape.center.y]])
                corners = np.array([[-x, x, x, -x], [y, y, -y, -y]])
                transformed_corners = rotation.dot(corners) + translation
                transformed_corners = transformed_corners.T.astype(int)
                cv2.fillPoly(image, pts=[transformed_corners],
                             color=shape.color)
            elif isinstance(shape, context.Circle):
                center = (int(shape.center.x), int(shape.center.y))
                image = cv2.circle(image, center, int(shape.radius),
                                   color=shape.color, thickness=-1)
            elif isinstance(shape, context.Text):
                center = (int(shape.center.x), int(shape.center.y))
                image = cv2.putText(image, shape.content, center,
                                    cv2.FONT_HERSHEY_SIMPLEX, shape.size,
                                    shape.color, 3, cv2.LINE_AA)
            elif isinstance(shape, context.Image):
                file_image = cv2.imread(shape.filepath, cv2.IMREAD_UNCHANGED)
                file_image = cv2.resize(file_image, (shape.width, shape.height))

                y1 = int(shape.center.y - shape.height / 2)
                y2 = int(y1 + file_image.shape[0])
                x1 = int(shape.center.x - shape.width / 2)
                x2 = int(x1 + file_image.shape[1])

                rgba = cv2.cvtColor(file_image, cv2.COLOR_RGB2RGBA)
                alpha_s = rgba[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s

                image_save = image.copy()
                for c in range(0, 3):
                    try:
                        image[y1:y2, x1:x2, c] = (
                                    alpha_s * file_image[:, :, c] +
                                    alpha_l * image[y1:y2, x1:x2, c])
                    except ValueError:
                        image = image_save

        self._display_frame(image)

    def _display_frame(self, image):
        cv2.imshow(Renderer.WINDOW_TITLE, image)

