from init import *


class Window:
    Screen = None

    def __init__(self, name, crop, scale, color):
        self.color = color
        self.crop = crop
        self.scale = scale
        self.name = name

    @staticmethod
    def Loop():
        bbox = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))
        Window.Screen = np.array(ImageGrab.grab(bbox=bbox))

    @staticmethod
    def LoopEnd():
        cv2.waitKey(25)

    def show(self, show):
        if show:
            cv2.imshow(self.name, self.getCapture())
        else:
            cv2.destroyWindow(self.name)

    def getCapture(self):
        temp_img = cv2.cvtColor(Window.Screen, self.color)
        temp_img = temp_img[self.crop[1]:self.crop[3], self.crop[0]:self.crop[2]]
        temp_img = imutils.resize(temp_img, width=self.scale)
        return temp_img
