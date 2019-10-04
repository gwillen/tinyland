import cv2
import numpy as np
import cv2.aruco as aruco
import toml

def load_config():
  projector = toml.load('./projector.toml')
  return projector

def correctImage(original_image, homography, projector):
  PROJECTOR_WIDTH = projector["PROJECTOR_WIDTH"]
  PROJECTOR_HEIGHT = projector["PROJECTOR_HEIGHT"]
  correctedImage = cv2.warpPerspective(original_image, homography, (PROJECTOR_WIDTH, PROJECTOR_HEIGHT)) # TODO: magic nums, use config constants
  correctedImage = cv2.flip(correctedImage, -1)
  return correctedImage

def calibrate(cap, projector):
  PROJECTOR_WIDTH = projector["PROJECTOR_WIDTH"]
  PROJECTOR_HEIGHT = projector["PROJECTOR_HEIGHT"]
  SRC_CORNERS = np.array(projector["SRC_CORNERS"])
  DEST_CORNERS = np.array(projector["DEST_CORNERS"])

  frame = cap.read()[1]

  # If we're at the end of the video, rewind. This comes into play when we're using a video file as input, as for testing offline.
  if frame is None:
    cap.set(cv2.CAP_PROP_POS_MSEC, 0)
    return

  # Escape hatch
  if cv2.waitKey(1) & 0xFF == ord('q'):
    exit()

  # Homography
  h, status = cv2.findHomography(SRC_CORNERS, DEST_CORNERS)

  # Correction
  image = correctImage(frame, h, projector)

  # Aruco - Find markers
  aruco_markers = aruco.detectMarkers(image, aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL))
  corners = aruco_markers[0]
  ids = aruco_markers[1]

  # Render
  BLACK = (0, 0, 0)
  WHITE = (255, 255, 255)
  image = cv2.rectangle(image, (0,0), (PROJECTOR_WIDTH, PROJECTOR_HEIGHT), BLACK, cv2.FILLED)
  # frame = aruco.drawDetectedMarkers(frame, corners, ids)
  image = aruco.drawDetectedMarkers(image, corners, ids)

  # Show it
  cv2.imshow("Tinycam", frame)
  cv2.imshow("Tinyland", image)

def printXY(_a, x, y, _b, _c):
  print("x: ", x)
  print("y: ", y)

def tinylandMouse(event, x, y, status, props):
  if event == cv2.EVENT_LBUTTONDBLCLK:
    cur = cv2.getWindowProperty("Tinyland", cv2.WND_PROP_FULLSCREEN)
    if cur == cv2.WINDOW_NORMAL:
      cv2.setWindowProperty("Tinyland", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
      cv2.setWindowProperty("Tinyland", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

if __name__ == "__main__":
  projector = load_config()
  cv2.namedWindow("Tinyland")
  cv2.namedWindow("Tinycam")
  cv2.setMouseCallback("Tinycam", printXY) # Useful when setting projection config.
  cv2.setMouseCallback("Tinyland", tinylandMouse) # Enable us to fullscreen it once it's on the correct desktop

  # Initialize video capture
  cap = None
  if projector["USE_CAMERA"]:
    # Hacky thing to find the right camera 🤷🏻‍♀️
    for i in range(5):
      cap = cv2.VideoCapture(1)
  else:
    cap = cv2.VideoCapture(projector["VIDEO_FILE_PATH"])

  while True:
    try:
      projector = load_config()
      calibrate(cap, projector)
    except KeyError:
      print('😭 Could not load config')
