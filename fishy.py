"""Fishy

Usage:  
  fishy.py -h | --help
  fishy.py -v | --version
  fishy.py -c | --configwin
  fishy.py -f | --fish [--ip=IPADDRESS] [HOOKTHRESHOLD] [MINIMUMCONFIDENCE]
  fishy.py (-s | --screencapture) FOLDERNAME
  fishy.py (-l | --learn) [--load] VALAMOUNT TESTAMOUNT

Options:
  -h, --help             Show this screen.
  -v, --version          Show version and exit.
  -c, --configwin        Configure the game window.
  -f, --fish             Start fishing.
  -s, --screencapture    Capture screen for learning.
  -l, --learn            Learn and create model.
  --load                 Load existing model to learn new data.


"""

VERSION = "0.0.2a 005"

print("Fishy "+VERSION+" for Elder Scrolls Online")
print("Loading, Please Wait...")

from docopt import docopt
arguments = docopt(__doc__)

import numpy as np
from PIL import ImageGrab
import cv2
import pyautogui
import time
from PIL import Image
import os
from random import shuffle
from tqdm import tqdm
import matplotlib.pyplot as plt
import sys
import math

import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import tensorflow as tf

import fishy_network as net
from threading import Timer


from pynput.keyboard import Key, Listener

controls = {"stop":[Key.f11,"f11"], "debug":[Key.f10,"f10"], "pause":[Key.f9,"f9"]}

stop = False
pause = False
debug = False

IMG_SIZE = 100
##IMG_SIZE_X = 350
##IMG_SIZE_Y = 284
LR = 1e-3


MODEL_NAME = 'learnstick-{}-{}.model'.format(LR, '6conv-basic-video')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR_HOOK = ROOT_DIR+r'\hook'
TRAIN_DIR_STICK = ROOT_DIR+r'\stick'
TRAIN_DIR_NONE = ROOT_DIR+r'\none'
TEST_DIR = ROOT_DIR+r'\test'

IMAGE_DIR = ROOT_DIR+"\\imgs\\"

STICK_TIMEOUT = 30.0 #secs
NONE_TIMEOUT = 5.0 #secs

if arguments['HOOKTHRESHOLD'] is not None:
    HOOK_THRESHOLD = int(arguments['HOOKTHRESHOLD'])
else:
    HOOK_THRESHOLD = 3

if arguments["MINIMUMCONFIDENCE"] is not None:
    MINIMUM_CONFIDENCE = float(arguments["MINIMUMCONFIDENCE"])
else:
    MINIMUM_CONFIDENCE = -1

IP_ADDRESS = arguments["--ip"]


def create_model():
    convnet = input_data(shape=[None, IMG_SIZE, IMG_SIZE, 1], name='input')

    convnet = conv_2d(convnet, 32, 2, activation='relu')
    convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 64, 2, activation='relu')
    convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 32, 2, activation='relu')
    convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 64, 2, activation='relu')
    convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 32, 2, activation='relu')
    convnet = max_pool_2d(convnet, 2)

    convnet = conv_2d(convnet, 64, 2, activation='relu')
    convnet = max_pool_2d(convnet, 2)

    convnet = fully_connected(convnet, 1024, activation='relu')
    convnet = dropout(convnet, 0.8)

    convnet = fully_connected(convnet, 3, activation='softmax')
    convnet = regression(convnet, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(convnet, tensorboard_dir='log')
    return model

def get_data_from(DIR, label):
    data = []
    for img in tqdm(os.listdir(DIR)):
        path = os.path.join(DIR,img)
        img = cv2.resize(cv2.imread(path, cv2.IMREAD_GRAYSCALE), (IMG_SIZE,IMG_SIZE))
        data.append([np.array(img), np.array(label)])
    return data

def create_train_data():
    training_data = []

    training_data.extend(get_data_from(TRAIN_DIR_HOOK,[1,0,0]))
    training_data.extend(get_data_from(TRAIN_DIR_STICK,[0,1,0]))
    training_data.extend(get_data_from(TRAIN_DIR_NONE,[0,0,1]))

    shuffle(training_data)
    #np.save('train_data.npy',training_data)
    return training_data

def create_test_data():
    testing_data = []
    i=0
    for img in tqdm(os.listdir(TEST_DIR)):
        path = os.path.join(TEST_DIR,img)
        img = cv2.resize(cv2.imread(path,cv2.IMREAD_GRAYSCALE), (IMG_SIZE,IMG_SIZE))
        testing_data.append([np.array(img),i])
        i+=1
    #np.save('test_data.npy',testing_data)
    return testing_data

def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked

def process_img(original_img):
    #processed_img = original_img
    processed_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    vertices = np.array([[290,216],[640,216],[640,500],[290,500]])
    processed_img = roi(processed_img,[vertices])
    croped_img = processed_img[216:500, 290:640]
    return croped_img

def save_img(data,foldername,no):
    rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
    im = Image.fromarray(rescaled)
    im.save(IMAGE_DIR+foldername+"\\"+foldername+str(no)+".png")

def create_test_data():
    testing_data = []
    i=0
    for img in tqdm(os.listdir(TEST_DIR)):
        path = os.path.join(TEST_DIR,img)
        img = cv2.resize(cv2.imread(path,cv2.IMREAD_GRAYSCALE), (IMG_SIZE,IMG_SIZE))
        testing_data.append([np.array(img),i])
        i+=1
    #np.save('test_data.npy',testing_data)
    return testing_data

def configureWindow():
    print("Depricated!!!, use fishy_config.py\npress q to quit")
    while(True):
        screen =  np.array(ImageGrab.grab(bbox=(0,40,800,600)))
        new_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        cv2.imshow('window', new_screen)
        
        k = cv2.waitKey(25) & 0xFF

        if k == ord('q') or k == ord('Q'):
            cv2.destroyAllWindows()
            break



def pressE():
    pyautogui.press('e')

def pullStick(fishCaught, timeToHook):
    print("HOOOOOOOOOOOOOOOOOOOOOOOK....... "+str(fishCaught)+" caught "+" in "+str(timeToHook)+" secs")
    pressE()
    #Timer(0.5, pressE).start()
    time.sleep(0.5)
    pressE()


def on_release(key):
    global stop, pause, debug

    if controls["pause"][0] == key:
        pause = not pause
        if pause:
            print("PAUSED")
        else:
            print("STARTED")

    elif controls["debug"][0] == key:
        debug = not debug

    elif controls["stop"][0] == key:
        stop = True

def startFishing():
    global stop, pause, debug
    
    pause = True
    showedControls = True
    debug = False
    stop = False
    hookCount = 0
    fishCaught = 0    
    model = create_model()
    model.load(MODEL_NAME)

    ctrl_help = controls["pause"][1]+": start or pause\n"+controls["debug"][1]+": start debug\n"+controls["stop"][1]+": quit\nHOOK_THRESHOLD is set to "+str(HOOK_THRESHOLD)+"\nMINIMUM_CONFIDENCE is set to "+str(MINIMUM_CONFIDENCE)

    print(ctrl_help)

    
    stickInitTime = time.time()
    noneInitTime = time.time()

    
    hookTime = time.time()

    use_net = False
    if IP_ADDRESS is not None:
        use_net = True
        net.initialize(IP_ADDRESS)

    holeDepleteSent = True
    noneTimeStarted = True

    timerStarted = False

    with Listener(on_release=on_release) as listener:
        while(True):    
            screen =  np.array(ImageGrab.grab(bbox=(0,40,800,600)))
            new_screen = process_img(screen)
            cv2.imshow('window', new_screen)

            processed_img = cv2.resize(new_screen, (IMG_SIZE,IMG_SIZE)).tolist()

            X = np.array(processed_img).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
            
            model_out = model.predict(X)[0]
            labelNum = np.argmax(model_out)



            if not pause:
                if labelNum == 0 and (MINIMUM_CONFIDENCE == -1 or model_out[0]>MINIMUM_CONFIDENCE):
                    #when 0 comes
                    hookCount+=1
                    
                    if hookCount >= HOOK_THRESHOLD:
                        #hooooked
                        hookCount=0
                        
                        fishCaught+=1
                        timeToHook = time.time() - stickInitTime
                        pullStick(fishCaught, timeToHook)

                        
                        
                else:
                    hookCount = 0

                if labelNum == 1:
                    if  not timerStarted:
                        stickInitTime = time.time()
                        timerStarted = True
                    if (time.time() - stickInitTime) >= STICK_TIMEOUT:
                        print("STICK TIMED OUT, THROWING AGAIN")
                        pressE()
                        timerStarted = False
                else:
                    timerStarted = False

                if labelNum == 2:
                    if not noneTimeStarted:
                        noneInitTime = time.time()
                        noneTimeStarted = True
                        holeDepleteSent = False
                    
                    if not holeDepleteSent and time.time() - noneInitTime >= NONE_TIMEOUT:
                        if fishCaught>0:
                            print("HOLE DEPLETED")
                            if use_net:
                                net.sendHoleDeplete(fishCaught)

                        fishCaught = 0
                        holeDepleteSent = True
                else:
                    noneTimeStarted = False
                                
                        
            if debug:
                print(str(labelNum)+'               '+str(model_out))
                showedControls = False
            else:
                if not showedControls:
                    showedControls = True
                    #os.system('cls')
                    print(ctrl_help)

            cv2.waitKey(25)

##            if k == ord('q') or k == ord('Q'):
##                cv2.destroyAllWindows()
##                break
##            if k == ord('p') or k == ord('P'):
##                pause = not pause
##                if pause:
##                    print("PAUSED")
##                    fishCaught = 0
##                else:
##                    print("STARTED")
##            if k == ord('d') or k == ord('D'):
##                debug = not debug

            if stop:
                cv2.destroyAllWindows()
                break
    
    
def screenCapture(foldername):
    global stop, pause, debug
    
    print("Press \n"+controls["pause"][1]+" to pause\n"+controls["stop"][1]+" to quit")
    imgNo = 0

    imgPath = IMAGE_DIR+foldername

    stop = False

    if not os.path.exists(imgPath):
        os.makedirs(imgPath)
    else:
        print("Folder already exists, move/delete it and try again")
        return

    with Listener(on_release=on_release) as listener:    
        while(True):
            screen =  np.array(ImageGrab.grab(bbox=(0,40,800,600)))
            new_screen = process_img(screen)
            cv2.imshow('window', new_screen)

            if not pause:
                save_img(new_screen,foldername,imgNo)

            imgNo+=1
            cv2.waitKey(25)
            if stop:
                cv2.destroyAllWindows()
                break

def closestMul(x):
    n = math.ceil(math.sqrt(x))
    m = math.ceil(x/n)
    return n,m

def learn(load,valamount,trainamount):
    if not load and os.path.exists('{}.meta'.format(MODEL_NAME)):
          print("Please move/delete your old model, and retry (--load to use existing model)")
          return

    train_data = create_train_data()
    tf.reset_default_graph()
    
    model = create_model()

    if load:
        if os.path.exists('{}.meta'.format(MODEL_NAME)):
            model.load(MODEL_NAME)
            print("Model Loaded")
        else:
            print("Could'nt find an existing model to load")

    train = train_data[:-valamount-trainamount]
    val = train_data[-valamount-trainamount:-trainamount]
    test_data = train_data[-trainamount:]

    X = np.array([i[0] for i in train]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    Y = [i[1] for i in train]

    test_x = np.array([i[0] for i in val]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    test_y = [i[1] for i in val]
    
    model.fit({'input': X}, {'targets': Y}, n_epoch=10, validation_set=({'input': test_x}, {'targets': test_y}),snapshot_step=500, show_metric=True, run_id=MODEL_NAME)
    model.save(MODEL_NAME)

    #test_data = create_test_data()

    fig = plt.figure()

    n,m = closestMul(trainamount)

    for num, data in enumerate(test_data):
        img_data = data[0]

        y=fig.add_subplot(n,m,num+1)
        orig = img_data
        data = img_data.reshape(IMG_SIZE, IMG_SIZE, 1)

        model_out = model.predict([data])[0]
        print(model_out)

        str_lable = str(np.argmax(model_out))

        y.imshow(orig, cmap='gray')
        plt.title(str_lable)
        y.axes.get_xaxis().set_visible(False)
        y.axes.get_yaxis().set_visible(False)
    plt.show()





if arguments["--configwin"]:
    configureWindow()
    
elif arguments["--fish"] :
    startFishing()
    
elif arguments["--screencapture"]:
    screenCapture(arguments["FOLDERNAME"])
    
elif arguments["--learn"]:
    learn(arguments["--load"],int(arguments["VALAMOUNT"]), int(arguments["TESTAMOUNT"]))

elif arguments["--version"]:
    print("Fishy "+VERSION+" For Elder Scrolls Online")

input("Press Enter to continue...")






