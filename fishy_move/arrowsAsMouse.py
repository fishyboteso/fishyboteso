from pynput.keyboard import Key, Listener
from pynput.mouse import Button, Controller

mouse = Controller()

moveValue =80

def on_press(key):
    if key == Key.up:
        mouse.move(0,-moveValue)
    elif key == Key.down:
        mouse.move(0,moveValue)
    elif key == Key.left:
        mouse.move(-moveValue,0)
    elif key == Key.right:
        mouse.move(moveValue,0)


# Collect events until released
with Listener(
        on_press=on_press,
        ) as listener:
    listener.join()
