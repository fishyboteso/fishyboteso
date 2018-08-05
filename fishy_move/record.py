from pynput import keyboard, mouse
import time

fo = open("record.txt", "w")

initTime = time.time()

class Key:
    pressed = False
    downTime = 0.0
    upTime = 0.0
    
    def __init__(self, c):
        #print(str(c)+" created")
        self.char = c
    
    def startTimer(self):
        self.downTime = time.time() - initTime
        self.pressed = True

    def stopTimer(self):
        self.upTime = time.time() - initTime
        self.pressed = False
        field = self.char+":"+str(self.downTime)+":"+str(self.upTime)
        fo.write(field+"\n")
        return field



w = Key('w')
a = Key('a')
s = Key('s')
d = Key('d')
e = Key('e')
space = Key("space")
up = Key('up')
down = Key("down")
left = Key("left")
right = Key("right")


keys = {'w':w, 'a':a, 's':s, 'd':d, 'e':e, keyboard.Key.space:space, keyboard.Key.up:up, keyboard.Key.down:down, keyboard.Key.left:left, keyboard.Key.right:right}


def on_press(key):
    try:
        i = keys.get(key.char, None)
        if i is not None and not i.pressed:
            i.startTimer()
          
    except AttributeError:

        i = keys.get(key, None)
        if i is not None and not i.pressed:
            i.startTimer()


def on_move(x, y):
    field = "mouse:"+str(x)+":"+str(y)+":"+str(time.time() - initTime)
    #print(field)
    fo.write(field+"\n")


def on_release(key):
##    print('{0} released'.format(
##        key))

    try:
        i = keys.get(key.char, None)
        if i is not None and i.pressed:
            print(str(i.stopTimer()))

    except AttributeError:
        i = keys.get(key, None)
        if i is not None and i.pressed:
            print(str(i.stopTimer()))
    
        if key == keyboard.Key.ctrl_r:
            # Stop listener
            return False

input("Press Enter when ready...")
print("get ready")
time.sleep(3)
print("goooooooo!!!!")

with  keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
    with mouse.Listener(on_move=on_move) as listener2:
        listener.join()

# Collect events until released


    


fo.close()
