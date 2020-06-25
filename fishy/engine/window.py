import logging

import cv2
import math
import win32gui
from win32api import GetSystemMetrics

import imutils
import numpy as np
from PIL import ImageGrab


class Window:
    """
    Records the game window, and allows to create instance to process it
    """
    Screen = None
    windowOffset = None
    titleOffset = None
    hwnd = None
    showing = False

    def __init__(self, crop=None, color=None, scale=None):
        """
        create a window instance with these pre process
        :param crop: [x1,y1,x2,y2] array defining the boundaries to crop
        :param color: color to use example cv2.COLOR_RGB2HSV
        :param scale: scaling the window
        """
        self.color = color
        self.crop = crop
        self.scale = scale

    @staticmethod
    def init(borderless: bool):
        """
        Executed once before the main loop,
        Finds the game window, and calculates the offset to remove the title bar
        """
        Window.hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")
        rect = win32gui.GetWindowRect(Window.hwnd)
        client_rect = win32gui.GetClientRect(Window.hwnd)
        Window.windowOffset = math.floor(((rect[2] - rect[0]) - client_rect[2]) / 2)
        Window.titleOffset = ((rect[3] - rect[1]) - client_rect[3]) - Window.windowOffset
        if borderless:
            Window.titleOffset = 0

    @staticmethod
    def loop():
        """
        Executed in the start of the main loop
        finds the game window location and captures it
        """
        Window.showing = False

        bbox = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))

        temp_screen = np.array(ImageGrab.grab(bbox=bbox))

        temp_screen = cv2.cvtColor(temp_screen, cv2.COLOR_BGR2RGB)

        rect = win32gui.GetWindowRect(Window.hwnd)
        crop = (rect[0] + Window.windowOffset, rect[1] + Window.titleOffset, rect[2] - Window.windowOffset,
                rect[3] - Window.windowOffset)

        Window.Screen = temp_screen[crop[1]:crop[3], crop[0]:crop[2]]

        if Window.Screen.size == 0:
            logging.info("Don't minimize or drag game window outside the screen")
            return False

        return True

    @staticmethod
    def loop_end():
        """
        Executed in the end of the game loop
        """
        cv2.waitKey(25)

        if not Window.showing:
            cv2.destroyAllWindows()

    def get_capture(self):
        """
        copies the recorded screen and then pre processes its
        :return: game window image
        """
        temp_img = Window.Screen

        if self.color is not None:
            temp_img = cv2.cvtColor(temp_img, self.color)

        if self.crop is not None:
            temp_img = temp_img[self.crop[1]:self.crop[3], self.crop[0]:self.crop[2]]

        if self.scale is not None:
            temp_img = cv2.resize(temp_img, (self.scale[0], self.scale[1]), interpolation=cv2.INTER_AREA)

        return temp_img

    def processed_image(self, func=None):
        """
        processes the image using the function provided
        :param func: function to process image
        :return: processed image
        """
        if func is None:
            return self.get_capture()
        else:
            return func(self.get_capture())

    def show(self, name, resize=None, func=None, ready_img=None):
        """
        Displays the processed image for debugging purposes
        :param ready_img: send ready image, just show the `ready_img` directly
        :param name: unique name for the image, used to create a new window
        :param resize: scale the image to make small images more visible
        :param func: function to process the image
        """
        if ready_img is None:
            img = self.processed_image(func)

            if resize is not None:
                img = imutils.resize(img, width=resize)
        else:
            img = ready_img
        cv2.imshow(name, img)

        Window.showing = True
