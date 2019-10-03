import cv2
import numpy as np
import cv2.aruco as aruco

# Config - Dependent on projector and camera position, so fiddle with these until they line up with the corners of your monitor
PROJECTOR_WIDTH = 1366
PROJECTOR_HEIGHT = 768

SRC_CORNERS = np.array([
  [101, 16], # top left
  [1004, 5], # top right
  [1005, 547], # bottom right
  [107, 555], # bottom left
])

# Projector dimensions
DEST_CORNERS = np.array([
  [0, 0], # top left
  [PROJECTOR_WIDTH, 0], # top right
  [PROJECTOR_WIDTH, PROJECTOR_HEIGHT], # bottom right
  [0, PROJECTOR_HEIGHT], # bottom left
])

VERTICAL_OFFSET = -45 # For title bar

def correctImage(original_image, homography, dimensions):
    correctedImage = cv2.warpPerspective(original_image, homography, (PROJECTOR_WIDTH, PROJECTOR_HEIGHT)) # TODO: magic nums, use config constants
    correctedImage = cv2.flip(correctedImage, -1)
    T = np.float32([[1, 0, 0], [0, 1, VERTICAL_OFFSET]])
    correctedImage = cv2.warpAffine(correctedImage, T, dimensions) 
    return correctedImage

def calibrate(cap):
  # Use camera 1, which is the attached usb camera.
  frame = cap.read()[1]
  scale_percent = 100
  width = int(frame.shape[1] * scale_percent / 100)
  height = int(frame.shape[0] * scale_percent / 100)
  dimensions = (width, height)

  # Resize the frame
  frame = cv2.resize(frame, dimensions, interpolation = cv2.INTER_AREA) # QUESTION: Does this need to happen here? Move to `correctImage`?

  # Escape hatch
  if cv2.waitKey(1) & 0xFF == ord('q'):
    exit()
  
  # Homography
  h, status = cv2.findHomography(SRC_CORNERS, DEST_CORNERS)

  # Correction
  image = correctImage(frame, h, dimensions)

  # Aruco - Find markers
  aruco_markers = aruco.detectMarkers(frame, aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL))
  corners = aruco_markers[0]
  ids = aruco_markers[1]

  # Render
  BLACK = (0, 0, 0)
  WHITE = (255, 255, 255)
  image = cv2.rectangle(image, (0,0), (PROJECTOR_WIDTH, PROJECTOR_HEIGHT), BLACK, cv2.FILLED)
  frame = aruco.drawDetectedMarkers(frame, corners, ids)
  image = aruco.drawDetectedMarkers(image, corners, ids)
  # image = cv2.circle(image, (100, 100), 30, WHITE, 5)
  
  # Show it
  cv2.imshow("Tinycam", frame)
  cv2.imshow("Tinyland", image)

def printXY(_a, x, y, _b, _c):
  print("x: ", x)
  print("y: ", y)

if __name__ == "__main__":
  # Hacky thing to find the right camera 🤷🏻‍♀️
  for i in range(5):
    cap = cv2.VideoCapture(1)
  
  cv2.namedWindow("Tinyland")
  cv2.namedWindow("Tinycam")
  cv2.setMouseCallback("Tinycam", printXY)
  
  while True:
    calibrate(cap)
