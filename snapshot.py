import cv2.aruco as aruco
from collections import namedtuple
import numpy as np


# Convenience class that allows indexing as well as x and y attribute access
XYPoint = namedtuple("XYPoint", ["x", "y"])


class Marker:
    """Base class for any detected physical objects.

    Args:
        x (int): x coordinate of center point
        y (int): y coordinate of center point
    Attribiutes:
        center (XYPoint): center point of marker
    """

    def __init__(self, x, y):
        self.center = XYPoint(x, y)


class ArucoMarker(Marker):

    def __init__(self, id, tl, tr, br, bl):
        [center_x, center_y] = np.median([np.array(tl), np.array(br)], axis=0)
        super().__init__(center_x, center_y)
        self.id = id
        self.tl = XYPoint(*tl)
        self.tr = XYPoint(*tr)
        self.bl = XYPoint(*bl)
        self.br = XYPoint(*br)
        self.rotation = np.degrees(np.arctan((self.tl.y - self.bl.y) /
                                             (self.tl.x - self.bl.x)))


class Snapshot:
    """Current state of physical markers on the landscape.

    Processes an image array and pulls out marker information for the user.

    Args:
        image (numpy.ndarray): A W x H x 3 matrix representing the image
            to process.
    Attributes:
        markers (dict<int, list<ArucoMarker>>): maps marker id to list of marker
            objects that match that id.
    """

    def __init__(self, image):
        self.image = image
        self.markers = self.detect_aruco()

    def detect_aruco(self):
        # Aruco - Find markers
        aruco_markers = aruco.detectMarkers(self.image, aruco.Dictionary_get(
            aruco.DICT_ARUCO_ORIGINAL))
        corners = aruco_markers[0]
        ids = aruco_markers[1]
        m = {}
        if ids is None:
            return m
        for aruco_id, corner in zip(ids, corners):
            id_key = int(aruco_id[0])
            [tl, tr, br, bl] = corner[0]
            m[id_key] = m.get(id_key, [])
            m[id_key].append(ArucoMarker(id_key, tl, tr, br, bl))
        return m
