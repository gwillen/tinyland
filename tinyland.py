import cv2
import numpy as np
import toml
import sys
import time

import context
import snapshot

def squaritude(c):
  _, _, w, h = cv2.boundingRect(c)
  if h > w:
      aspect = w/h
  else:
      aspect = h/w
  rectitude = cv2.contourArea(c) / (w*h)
  return aspect * rectitude


class Landscape:
  WINDOW_TITLE = "Tinyland"

  def __init__(self):
    self.camera = None
    self.projector = None
    self.homography = np.eye(3)

  def load_config(self, config_file):
    self.projector = toml.load(config_file)

  def toggle_fullscreen(self):
    cur = cv2.getWindowProperty(self.WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN)
    if cur == cv2.WINDOW_NORMAL:
      cv2.setWindowProperty(self.WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
      cv2.setWindowProperty(self.WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

  def camera_to_projector_space(self, image):
    for i in range(5):
      try:
        image = cv2.warpPerspective(image, self.homography, (self.projector["PROJECTOR_WIDTH"], self.projector["PROJECTOR_HEIGHT"]))
        break
      except cv2.error:
        print("Warp perspective failed. Attempt #%s" % (i + 1))
        time.sleep(1)
        if i == 5:
            print("Warp perspective failed for good 😭. Exiting early.")
            sys.exit()

    if(self.projector["FLIP_PROJECTION"]):
      image = cv2.flip(image, -1)
    return image

  def get_raw_frame(self):
    frame = self.camera.read()[1]

    # If we're at the end of the video, rewind. This comes into play when we're using a video file as input, as for testing offline.
    if frame is None and not self.projector["USE_CAMERA"]:
      self.camera.set(cv2.CAP_PROP_POS_MSEC, 0)
      frame = self.camera.read()[1]

    return frame

  def get_key(self):
    key = cv2.waitKey(1)
    if key == -1:
      return None
    return chr(key & 0xFF)

  def display_markers(self, image):
    PROJECTOR_WIDTH = self.projector["PROJECTOR_WIDTH"]
    PROJECTOR_HEIGHT = self.projector["PROJECTOR_HEIGHT"]

    # Display calibration markers until we find them
    M_SZ = 40
    marker = np.zeros((M_SZ, M_SZ, 3), dtype=np.uint8)
    cv2.rectangle(marker, (0, 0), (M_SZ, M_SZ), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(marker, (10, 10), (M_SZ-10, M_SZ-10), (0, 0, 0), cv2.FILLED)

    image[0:M_SZ, 0:M_SZ] = marker
    marker = cv2.rotate(marker, cv2.ROTATE_90_CLOCKWISE)
    image[0:M_SZ, PROJECTOR_WIDTH-M_SZ:PROJECTOR_WIDTH] = marker
    marker = cv2.rotate(marker, cv2.ROTATE_90_CLOCKWISE)
    image[PROJECTOR_HEIGHT-M_SZ:PROJECTOR_HEIGHT, PROJECTOR_WIDTH-M_SZ:PROJECTOR_WIDTH] = marker
    marker = cv2.rotate(marker, cv2.ROTATE_90_CLOCKWISE)
    image[PROJECTOR_HEIGHT-M_SZ:PROJECTOR_HEIGHT, 0:M_SZ] = marker

  def find_corners(self, frame):
    PROJECTOR_WIDTH = self.projector["PROJECTOR_WIDTH"]
    PROJECTOR_HEIGHT = self.projector["PROJECTOR_HEIGHT"]

    # Search for our calibration markers
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rv, frame_thresh = cv2.threshold(frame_gray, 185, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(frame_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = hierarchy[0]

    markers = []
    for i in range(len(contours)):
      # opencv contour hierarchy: [Next, Previous, First_Child, Parent]
      # https://docs.opencv.org/3.4/d9/d8b/tutorial_py_contours_hierarchy.html
      child_idx = hierarchy[i][2]
      next_child_idx = hierarchy[child_idx][1]

      # Look for contours with exactly one child of plausible size
      if child_idx != -1 and next_child_idx == -1:
        area = cv2.contourArea(contours[i])
        child_area = cv2.contourArea(contours[child_idx])

        if (squaritude(contours[i]) > 0.75 and
            squaritude(contours[child_idx]) > 0.5 and
            child_area and
            area / child_area < 10 and
            area / child_area > 2):
          markers.append(i)

    if len(markers) == 4:
      # Assume we've found our markers - take a convex hull and check that it's a quadrilateral
      all_points = []
      for c in [contours[i] for i in markers]:
        all_points.extend(c)
      boundary = cv2.convexHull(np.array(all_points))
      boundary = cv2.approxPolyDP(boundary, 25, True)
      # Not sure why this is necessary
      boundary = boundary[:,0]
      if len(boundary) == 4:
        # This has to be the dumbest possible way to sort four points clockwise from top left
        point1 = [p for p in boundary if p[0] < PROJECTOR_WIDTH/2 and p[1] < PROJECTOR_HEIGHT/2]
        point2 = [p for p in boundary if p[0] > PROJECTOR_WIDTH/2 and p[1] < PROJECTOR_HEIGHT/2]
        point3 = [p for p in boundary if p[0] > PROJECTOR_WIDTH/2 and p[1] > PROJECTOR_HEIGHT/2]
        point4 = [p for p in boundary if p[0] < PROJECTOR_WIDTH/2 and p[1] > PROJECTOR_HEIGHT/2]
        if len(point1) == 1 and len(point2) == 1 and len(point3) == 1 and len(point4) == 1:
          final_corners = np.array([point1[:], point2[:], point3[:], point4[:]])
          # It's slightly hacky for us to mix up our state and our config in this way.
          return final_corners
    return None

  def display_frame(self, image):
    cv2.imshow(self.WINDOW_TITLE, image)

  def initialize_camera(self):
    if self.projector["USE_CAMERA"]:
      try:
        # Grab camera from config
        self.camera = cv2.VideoCapture(self.projector["VIDEO_CAPTURE_INDEX"])
      except KeyError:
        # If camera doesn't exist in config, prompt user to select one of the connected cameras.
        self.camera = select_camera()
    else:
      self.camera = cv2.VideoCapture(self.projector["VIDEO_FILE_PATH"])

  def get_snapshot(self):
    """Process self.camera image into a Snapshot.

    Returns:
      snap (snapshot.Snapshot): snapshot generated from self.camera image.
    """
    SRC_CORNERS = np.array(self.projector["SRC_CORNERS"])
    DEST_CORNERS = np.array(self.projector["DEST_CORNERS"])
    frame = self.get_raw_frame()
    if frame is not None:
      cv2.imshow("Tinycam", frame)

    # TODO: move user input handling out of this method
    # Handle keypress events
    key = self.get_key()
    if key == 'q':
      sys.exit()
    if key == 'f':
      self.toggle_fullscreen()
    if key == 'c':
      self.projector["CALIBRATE"] = True

    if self.projector.get("CALIBRATE"):
      corners = self.find_corners(frame)
      if corners is not None:
        SRC_CORNERS = corners
        self.projector["SRC_CORNERS"] = corners
        self.projector["CALIBRATE"] = False
        self.homography, status = cv2.findHomography(SRC_CORNERS, DEST_CORNERS)

    image = self.camera_to_projector_space(frame)
    snap = snapshot.Snapshot(image)

    return snap

  def project(self, ctx):
    """Display the draw context to the landscape.

    Process all shapes in the context and render resulting image.

    Args:
      ctx (context.DrawingContext): A context with shapes to draw
    """
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    image = np.zeros((self.projector["PROJECTOR_HEIGHT"], self.projector["PROJECTOR_WIDTH"], 3), np.uint8)
    for shape in ctx.shapes:
      if isinstance(shape, context.Rectangle):
        image = cv2.rectangle(image,
                      (int(shape.center.x - shape.width / 2), int(shape.center.y - shape.height / 2)),
                      (int(shape.center.x + shape.width / 2), int(shape.center.y + shape.height / 2)),
                      WHITE, cv2.FILLED)
      elif isinstance(shape, context.Text):
        center = (int(shape.center.x), int(shape.center.y))
        image = cv2.putText(image, shape.content, center, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)

    if self.projector.get("CALIBRATE"):
      self.display_markers(image)

    # Show it
    self.display_frame(image)


def printXY(_a, x, y, _b, _c):
  print("x: ", x)
  print("y: ", y)


def select_camera():
  """Get OpenCV VideoCapture camera. Prompt user if multiple cameras found.

  Returns:
    cv2.VideoCapture instance of the selected camera.
  """
  # Get list of all connected cameras
  cameras = []
  while True:
    cap = cv2.VideoCapture(len(cameras))
    _, frame = cap.read()
    if frame is not None:
      cameras.append(cap)
    else:
      break

  if len(cameras) == 0:
    print("No VideoCapture devices detected!")
    return None
  elif len(cameras) == 1:
    print("Found one camera, so using that one.")
    return cameras[0]
  else:
    # Open user flow to select camera
    print("Press n and p to cycle through connected cameras. Press s to select.")
    SELECT_CAM_WINDOW = "Select Camera"
    cv2.namedWindow(SELECT_CAM_WINDOW)
    cur_index = 0
    while True:
      # Handle keypress events
      key = cv2.waitKey(1)
      if key & 0xFF == ord('s'):
        cv2.destroyWindow(SELECT_CAM_WINDOW)
        return cameras[cur_index]
      if key & 0xFF == ord('n'):
        cur_index = (cur_index - 1) % len(cameras)
      if key & 0xFF == ord('p'):
        cur_index = (cur_index - 1) % len(cameras)

      cv2.imshow(SELECT_CAM_WINDOW, cameras[cur_index].read()[1])

  
def run(app):
  l = Landscape()
  l.load_config("./config.toml")
  cv2.namedWindow("Tinycam")
  cv2.namedWindow(Landscape.WINDOW_TITLE)
  cv2.setMouseCallback("Tinycam", printXY) # Useful when setting projection config.
  cv2.setWindowProperty(Landscape.WINDOW_TITLE, cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_NORMAL) # Allow window to be fullsized by both the OS window controls and OpenCV
  l.initialize_camera()
  
  while True:
    snap = l.get_snapshot()
    ctx = context.DrawingContext(l.projector["PROJECTOR_WIDTH"], l.projector["PROJECTOR_HEIGHT"])

    # Run the user defined app
    app(snap, ctx)

    # Render projection
    l.project(ctx)
