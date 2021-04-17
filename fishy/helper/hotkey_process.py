import time
from threading import Thread

import mouse
from multiprocessing import Process, Queue


def event_triggered(queue, e):
    if not (type(e) == mouse.ButtonEvent and e.event_type == "up" and e.button == "left"):
        return

    # call the parent function here
    queue.put("left click")


def run(inq, outq):
    mouse.hook(lambda e: event_triggered(outq, e))

    stop = False
    while not stop:
        time.sleep(1)
        if inq.get() == "stop":
            stop = True


class HotKey:
    def __init__(self):
        self.inq = Queue()
        self.outq = Queue()

        self.process = Process(target=run, args=(self.inq, self.outq))

    def event_loop(self, func):
        while True:
            msg = self.outq.get()
            if msg == "left click":
                func()

    def start_process(self, func):
        self.process.start()
        Thread(target=self.event_loop, args=(func,)).start()

    def stop(self):
        self.inq.put("stop")
        self.process.join()
        print("hotkey process ended")
