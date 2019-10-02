import cv2
import numpy as np

# Config - Dependent on projector and camera position, so fiddle with these until they line up with the corners of your monitor
SRC_CORNERS = np.array([
  [119, 82], # top left
  [1016, 47], # top right
  [1031, 585], # bottom right
  [136, 615], # bottom left
])

# Projector dimensions
DEST_CORNERS = np.array([
  [0, 0], # top left
  [1366, 0], # top right
  [1366, 768], # bottom right
  [0, 768], # bottom left
])

VERTICAL_OFFSET = 31 # For title bar

def corner_points_to_point(corner):
  return corner[0][0]

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
  warpedImage = cv2.warpPerspective(frame, homography, (1366, 768)) # TODO: magic nums, use config constants
  warpedImage = cv2.flip(warpedImage, -1)
  cv2.imshow("Tinyland", warpedImage)

def printXY(_a, x, y, _b, _c):
  print("x: ", x)
  print("y: ", y)

if __name__ == "__main__":
  # Hacky thing to find the right camera 🤷🏻‍♀️
  for i in range(5):
    cap = cv2.VideoCapture(1)
  
  cv2.namedWindow("Tinyland")
  cv2.namedWindow("Tinycam")
  # cv2.setMouseCallback("Tinycam", printXY)
  
  while True:
    calibrate(cap)
