from log import *


class Window:
    Screen = None
    wins = []

    def __init__(self, name, crop, color, scale=None):
        self.color = color
        self.crop = crop
        self.scale = scale
        self.name = name

        self.showed = False
        Window.wins.append(self)

    @staticmethod
    def Loop():
        bbox = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))
        Window.Screen = np.array(ImageGrab.grab(bbox=bbox))


    @staticmethod
    def LoopEnd():
        cv2.waitKey(25)

        for w in Window.wins:

            if not w.showed:
                cv2.destroyWindow(w.name)

            w.showed = False

    def getCapture(self):
        temp_img = cv2.cvtColor(Window.Screen, self.color)
        temp_img = temp_img[self.crop[1]:self.crop[3], self.crop[0]:self.crop[2]]

        if self.scale is not None:
            temp_img = cv2.resize(temp_img, (self.scale[0], self.scale[1]), interpolation=cv2.INTER_AREA)

        return temp_img

    def processedImage(self, func=None):
        if func is None:
            return self.getCapture()
        else:
            return func(self.getCapture())

    def show(self, resize=None, func=None):
        img = self.processedImage(func)

        if resize is not None:
            img = imutils.resize(img, width=resize)

        cv2.imshow(self.name, img)

        self.showed = True
