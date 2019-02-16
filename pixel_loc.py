from fishing_event import *


def GetKeypointFromImage(img):
    # Setup SimpleBlobDetector parameters.
    hsvImg = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower = (99, 254, 100)
    upper = (100, 255, 101)
    mask = cv2.inRange(hsvImg, lower, upper)

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 255

    params.filterByColor = True
    params.blobColor = 255

    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False

    params.filterByArea = True
    params.minArea = 10.0

    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(mask)

    if len(keypoints) <= 0:
        return None

    return int(keypoints[0].pt[0]), int(keypoints[0].pt[1])


class PixelLoc:
    val = None

    @staticmethod
    def config():
        win = Window()
        t = GetKeypointFromImage(win.getCapture())

        if t is None:
            return False

        PixelLoc.val = (t[0], t[1], t[0] + 1, t[1] + 1)
        return True
