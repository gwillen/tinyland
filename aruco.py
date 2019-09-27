import cv2
import cv2.aruco as aruco


def do_arcuo_thing(cap):
  frame = cap.read()[1]
  scale_percent = 100
  width = int(frame.shape[1] * scale_percent / 100)
  height = int(frame.shape[0] * scale_percent / 100)
  dimemsions = (width, height)
  frame = cv2.resize(frame, dimemsions, interpolation = cv2.INTER_AREA)
  markers = aruco.detectMarkers(frame, aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL))
  frame = aruco.drawDetectedMarkers(frame, markers[0], markers[1])
  cv2.imshow("aruco test", frame)

  # cv2.imshow("", frame)
  # cv2.waitKey()

  if cv2.waitKey(1) & 0xFF == ord('q'):
    exit()
  

if __name__ == "__main__":
  cap = cv2.VideoCapture(0)
  cv2.namedWindow("aruco test")
  while True:
    do_arcuo_thing(cap)