import cv2
import cv2.aruco as aruco


def do_arcuo_thing(cap):
  frame = cap.read()[1]
  cv2.imshow("aruco test", frame)
  # img = cv2.imread("aruco-test-image-3-7.jpg", cv2.IMREAD_UNCHANGED)

  # scale_percent = 100
  # width = int(img.shape[1] * scale_percent / 100)
  # height = int(img.shape[0] * scale_percent / 100)
  # dim = (width, height)
  # img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

  # markers = aruco.detectMarkers(img, aruco.Dictionary_get(aruco.DICT_4X4_50))
  # img = aruco.drawDetectedMarkers(img, markers[0], markers[1])

  # cv2.imshow("", img)
  # cv2.waitKey()
  
  if cv2.waitKey(1) & 0xFF == ord('q'):
    exit()
  

if __name__ == "__main__":
  cap = cv2.VideoCapture(0)
  cv2.namedWindow("aruco test")
  while True:
    do_arcuo_thing(cap)