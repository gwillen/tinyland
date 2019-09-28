import cv2
import cv2.aruco as aruco
import numpy as np

def corner_points_to_point(corner):
  return corner[0][0]

def do_aruco_thing(cap):
  corner_ids = [393, 19, 193, 979]
  # Use camera 1, which is the attached usb camera.
  frame = cap.read()[1]

  # Resize the frame
  scale_percent = 100
  width = int(frame.shape[1] * scale_percent / 100)
  height = int(frame.shape[0] * scale_percent / 100)
  dimensions = (width, height)
  frame = cv2.resize(frame, dimensions, interpolation = cv2.INTER_AREA)

  # Find markers and draw them
  aruco_markers = aruco.detectMarkers(frame, aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL))
  frame = cv2.rectangle(frame, (0,0), dimensions, (0,0,0), cv2.FILLED)
  corners = aruco_markers[0]
  ids = aruco_markers[1]
  if ids is not None:
    unique_ids = { id[0] : indx for indx, id in enumerate(ids) }
  else:
    unique_ids = {}

  # if 393 in unique_ids and 19 in unique_ids and 193 in unique_ids and 979 in unique_ids:
  if all([id in unique_ids for id in corner_ids]):
    yfacty = .7
    xfacty = 1
    src = np.array(
      [
        corner_points_to_point(corners[unique_ids[393]]),
        corner_points_to_point(corners[unique_ids[19]]),
        corner_points_to_point(corners[unique_ids[193]]),
        corner_points_to_point(corners[unique_ids[979]])
      ]
    )
    dst = np.array(
      [
        [0, 0],
        [width * xfacty, 0],
        [0, height * yfacty],
        [width * xfacty, height * yfacty]
      ]
    )
    do_aruco_thing.homography = cv2.findHomography(src, dst)[0]

  for idx, id in enumerate(ids):
    if id not in corner_ids:
      pt = corner_points_to_point(corners[idx])
      pt = (pt[0], pt[1], 1)
      pt = np.dot(do_aruco_thing.homography, pt)
      pt = (int(pt[0]), int(pt[1]))
      frame = cv2.circle(frame, pt, 40, (0, 0, 255))

  frame = aruco.drawDetectedMarkers(frame, corners, ids)

  # Show it
  cv2.imshow("aruco test", frame)
  
  # Escape hatch
  if cv2.waitKey(1) & 0xFF == ord('q'):
    exit()

if __name__ == "__main__":
  for i in range(5):
    cap = cv2.VideoCapture(1)
  do_aruco_thing.homography = np.identity
  cv2.namedWindow("aruco test")
  while True:
    do_aruco_thing(cap)
