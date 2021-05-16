from event_scheduler import EventScheduler
from fishy.web import web


# noinspection PyPep8Naming
class active:
    _scheduler: EventScheduler = None

    @staticmethod
    def init():
        if active._scheduler:
            return

        active._scheduler = EventScheduler()
        active._scheduler.start()

    @staticmethod
    def start():
        active._scheduler.enter_recurring(60, 1, web.ping)

    @staticmethod
    def stop():
        active._scheduler.stop(hard_stop=True)
