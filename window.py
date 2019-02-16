from log import *


class Window:
    Screen = None
    windowOffset = None
    titleOffset = None
    hwnd = None
    showing = False

    def __init__(self, crop=None, color=None, scale=None):
        self.color = color
        self.crop = crop
        self.scale = scale

    @staticmethod
    def Init():
        try:
            Window.hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")
            rect = win32gui.GetWindowRect(Window.hwnd)
            clientRect = win32gui.GetClientRect(Window.hwnd)
            Window.windowOffset = math.floor(((rect[2] - rect[0]) - clientRect[2]) / 2)
            Window.titleOffset = ((rect[3] - rect[1]) - clientRect[3]) - Window.windowOffset
        except pywintypes.error:
            print("Game window not found")
            quit()

    @staticmethod
    def Loop():
        Window.showing = False

        bbox = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))

        tempScreen = np.array(ImageGrab.grab(bbox=bbox))

        tempScreen = cv2.cvtColor(tempScreen, cv2.COLOR_BGR2RGB)

        rect = win32gui.GetWindowRect(Window.hwnd)
        crop = (rect[0] + Window.windowOffset, rect[1] + Window.titleOffset, rect[2] - Window.windowOffset,
                           rect[3] - Window.windowOffset)

        Window.Screen = tempScreen[crop[1]:crop[3], crop[0]:crop[2]]

        if Window.Screen.size == 0:
            print("Don't drag game window outside the screen")
            quit(1)

    @staticmethod
    def LoopEnd():
        cv2.waitKey(25)

        if not Window.showing:
            cv2.destroyAllWindows()

    def getCapture(self):
        temp_img = Window.Screen

        if self.color is not None:
            temp_img = cv2.cvtColor(temp_img, self.color)

        if self.crop is not None:
            temp_img = temp_img[self.crop[1]:self.crop[3], self.crop[0]:self.crop[2]]

        if self.scale is not None:
            temp_img = cv2.resize(temp_img, (self.scale[0], self.scale[1]), interpolation=cv2.INTER_AREA)

        return temp_img

    def processedImage(self, func=None):
        if func is None:
            return self.getCapture()
        else:
            return func(self.getCapture())

    def show(self, name, resize=None, func=None):
        img = self.processedImage(func)

        if resize is not None:
            img = imutils.resize(img, width=resize)

        cv2.imshow(name, img)

        Window.showing = True
