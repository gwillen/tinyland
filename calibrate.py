import cv2
import numpy as np

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

def calibrate(cap):
  # Use camera 1, which is the attached usb camera.
  frame = cap.read()[1]

  # Resize the frame
  scale_percent = 100
  width = int(frame.shape[1] * scale_percent / 100)
  height = int(frame.shape[0] * scale_percent / 100)
  dimensions = (width, height)
  frame = cv2.resize(frame, dimensions, interpolation = cv2.INTER_AREA)

  # Show it
  cv2.imshow("Tinycam", frame)
  
  # Escape hatch
  if cv2.waitKey(1) & 0xFF == ord('q'):
    exit()
  
  # Homography stuff
  homography, status = cv2.findHomography(SRC_CORNERS, DEST_CORNERS)
  correctedImage = cv2.warpPerspective(frame, homography, (PROJECTOR_WIDTH, PROJECTOR_HEIGHT)) # TODO: magic nums, use config constants
  correctedImage = cv2.flip(correctedImage, -1)

  T = np.float32([[1, 0, 0], [0, 1, VERTICAL_OFFSET]])
  correctedImage = cv2.warpAffine(correctedImage, T, (width, height)) 
  BLACK = (0, 0, 0)
  correctedImage = cv2.rectangle(correctedImage, (0,0), (PROJECTOR_WIDTH, PROJECTOR_HEIGHT), BLACK, cv2.FILLED)
  cv2.imshow("Tinyland", correctedImage)

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
