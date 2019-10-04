import cv2
import numpy as np
import cv2.aruco as aruco
import toml

def load_config():
  projector = toml.load('./config.toml')
  return projector

def correctImage(original_image, homography, projector):
  PROJECTOR_WIDTH = projector["PROJECTOR_WIDTH"]
  PROJECTOR_HEIGHT = projector["PROJECTOR_HEIGHT"]
  correctedImage = cv2.warpPerspective(original_image, homography, (PROJECTOR_WIDTH, PROJECTOR_HEIGHT)) # TODO: magic nums, use config constants
  return correctedImage

def toggle_fullscreen():
  cur = cv2.getWindowProperty("Tinyland", cv2.WND_PROP_FULLSCREEN)
  if cur == cv2.WINDOW_NORMAL:
    cv2.setWindowProperty("Tinyland", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
  else:
    cv2.setWindowProperty("Tinyland", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

def squaritude(c):
  _, _, w, h = cv2.boundingRect(c)
  if h > w:
      aspect = w/h
  else:
      aspect = h/w
  rectitude = cv2.contourArea(c) / (w*h)
  return aspect * rectitude

def do_frame(cap, projector):
  PROJECTOR_WIDTH = projector["PROJECTOR_WIDTH"]
  PROJECTOR_HEIGHT = projector["PROJECTOR_HEIGHT"]
  SRC_CORNERS = np.array(projector["SRC_CORNERS"])
  DEST_CORNERS = np.array(projector["DEST_CORNERS"])
  FLIP_PROJECTION = np.array(projector["FLIP_PROJECTION"])

  frame = cap.read()[1]

  # If we're at the end of the video, rewind. This comes into play when we're using a video file as input, as for testing offline.
  if frame is None:
    cap.set(cv2.CAP_PROP_POS_MSEC, 0)
    return

  # Handle keypress events
  key = cv2.waitKey(1)
  if key & 0xFF == ord('q'):
    exit()
  if key & 0xFF == ord('f'):
    toggle_fullscreen()
  if key & 0xFF == ord('c'):
    projector["CALIBRATE"] = True

  if projector.get("CALIBRATE"):
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
          SRC_CORNERS = np.array([point1[:], point2[:], point3[:], point4[:]])
          # It's slightly hacky for us to mix up our state and our config in this way.
          projector["SRC_CORNERS"] = SRC_CORNERS
          projector["CALIBRATE"] = False

      cv2.drawContours(frame, [boundary], 0, (0, 255, 0), 2)

  # Homography
  h, status = cv2.findHomography(SRC_CORNERS, DEST_CORNERS)

  # Correction
  image = correctImage(frame, h, projector)
  if(FLIP_PROJECTION):
    image = cv2.flip(image, -1)

  # Aruco - Find markers
  aruco_markers = aruco.detectMarkers(image, aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL))
  corners = aruco_markers[0]
  ids = aruco_markers[1]

  # Render
  BLACK = (0, 0, 0)
  WHITE = (255, 255, 255)
  image = cv2.rectangle(image, (0,0), (PROJECTOR_WIDTH, PROJECTOR_HEIGHT), BLACK, cv2.FILLED)
  image = aruco.drawDetectedMarkers(image, corners, ids)

  if projector.get("CALIBRATE"):
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

  # Show it
  cv2.imshow("Tinycam", frame)
  cv2.imshow("Tinyland", image)

def printXY(_a, x, y, _b, _c):
  print("x: ", x)
  print("y: ", y)

if __name__ == "__main__":
  projector = load_config()
  cv2.namedWindow("Tinyland")
  cv2.namedWindow("Tinycam")
  cv2.setMouseCallback("Tinycam", printXY) # Useful when setting projection config.
  cv2.setWindowProperty("Tinyland", cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_NORMAL) # Allow window to be fullsized by both the OS window controls and OpenCV

  # Initialize video capture
  cap = None
  if projector["USE_CAMERA"]:
    # Hacky thing to find the right camera 🤷🏻‍♀️
    for i in range(5):
      cap = cv2.VideoCapture(1)
  else:
    cap = cv2.VideoCapture(projector["VIDEO_FILE_PATH"])

  while True:
    do_frame(cap, projector)
