from PIL import ImageGrab, Image
import cv2
import pytesseract
import numpy as np
from pynput.keyboard import Key, Controller, Listener
import json
import _thread
import time

def getSizeFromConfig():
    config = json.load(open("config.json"))
    return config["box"]["x"],config["box"]["y"],config["box"]["w"],config["box"]["h"]

def process_img(screen):
    img = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    return img

def getValuesFromImage(cvImg):
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
    tessdata_dir_config = '--tessdata-dir "C:/Program Files (x86)/Tesseract-OCR/" -c tessedit_char_whitelist=0123456789.'

    img = (255 - cvImg)
    img = Image.fromarray(img)
    text = pytesseract.image_to_string(img, lang="eng", config=tessdata_dir_config)

    text.replace(" ","")

    print(text)
    #cv2.imshow('gray_image', img)

    vals = text.split("\n")

    try:
        return float(vals[0]), float(vals[1]), float(vals[2])
    except Exception:
        time.sleep(0.5)
        return getValues()

#1
def getValues():
    keyboard = Controller()
    keyboard.press(Key.enter)
    keyboard.type("/getcoords")
    keyboard.press(Key.enter)

    time.sleep(0.5)

    screen = np.array(ImageGrab.grab())
    screen = screen[y:y + h, x:x + w]

    new_screen = process_img(screen)


    #cv2.imshow('window', new_screen)
    i,j,a = getValuesFromImage(new_screen)
    #print(str(i)+" "+str(j)+" "+str(a))
    return x,y,a


def configureValuesBox():
    _thread.start_new_thread(changeSizeFromConsole, ())

    screen = np.array(ImageGrab.grab())
    print(str(screen.shape[1])+"x"+str(screen.shape[0]))
    print(str(x)+" "+str(y)+" "+str(w)+" "+str(h))

    while True:
        screen = np.array(ImageGrab.grab())
        screen = screen[y:y+h, x:x+w]

        new_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

        cv2.imshow('window', new_screen)

        k = cv2.waitKey(25) & 0xFF

        if k == ord('q') or k == ord('Q'):
            updateBoxInConfig()
            cv2.destroyAllWindows()
            break


def updateBoxInConfig():
    global x,y,w,h

    with open("config.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["box"]["x"] = x
    data["box"]["y"] = y
    data["box"]["w"] = w
    data["box"]["h"] = h

    with open("config.json", "w") as jsonFile:
        json.dump(data, jsonFile)

def changeSizeFromConsole():
    global x, y, w, h

    while True:
        sizeValsStr = input()
        sizeVals = sizeValsStr.split(" ")
        x,y,w,h = int(sizeVals[0]),int(sizeVals[1]),int(sizeVals[2]),int(sizeVals[3])



x,y,w,h = getSizeFromConfig()

def on_release(key):
    if key == Key.f9:
       getValues()

with Listener(
        on_release=on_release) as listener:
    listener.join()

# configureValuesBox()