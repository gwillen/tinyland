import cv2
import cv2.aruco as aruco
import numpy as np

# Config - dependent on projector and table, etc
X_FACTOR_TOP_LEFT = 0.087890625 
Y_FACTOR_TOP_LEFT = 0.078125
X_FACTOR_BOTTOM_LEFT = 0.8
Y_FACTOR_BOTTOM_LEFT = 0.6

def corner_points_to_point(corner):
  return corner[0][0]

def do_aruco_thing(cap):
  # Use camera 1, which is the attached usb camera.
  frame = cap.read()[1]

  # Resize the frame
  scale_percent = 50
  width = int(frame.shape[1] * scale_percent / 100)
  height = int(frame.shape[0] * scale_percent / 100)
  dimensions = (width, height)
  frame = cv2.resize(frame, dimensions, interpolation = cv2.INTER_AREA)

  def draw_corner(frame, x_factor, y_factor):
    corner_position = (int(x_factor * width), int(y_factor * height))
    frame = cv2.circle(frame, corner_position, 10, (200, 100, 100), 5)
    return frame

  frame = draw_corner(frame, X_FACTOR_TOP_LEFT, Y_FACTOR_TOP_LEFT)
  frame = draw_corner(frame, X_FACTOR_BOTTOM_LEFT, Y_FACTOR_BOTTOM_LEFT)
  
  

  # Find homography
  # src = np.array(
  #   [
  #     corner_points_to_point(some_corner),
  #     corner_points_to_point(some_corner),
  #     corner_points_to_point(some_corner),
  #     corner_points_to_point(some_corner),
  #   ]
  # )
  # dst = np.array(
  #   [
  #     corner_points_to_point(some_corner),
  #     corner_points_to_point(some_corner),
  #     corner_points_to_point(some_corner),
  #     corner_points_to_point(some_corner),
  #   ]
  # )
  # do_aruco_thing.homography = cv2.findHomography(src, dst)[0]

  # Show it
  cv2.imshow("aruco test", frame)
  
  # Escape hatch
  if cv2.waitKey(1) & 0xFF == ord('q'):
    exit()

if __name__ == "__main__":
  # Hacky thing to find the right camera, ugh
  for i in range(5):
    cap = cv2.VideoCapture(1)
  
  # Init the homography matrix to the "identity matrix"
  do_aruco_thing.homography = np.identity
  
  cv2.namedWindow("aruco test")
  
  while True:
    do_aruco_thing(cap)
