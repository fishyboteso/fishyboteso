import logging

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
        logging.debug("active scheduler initialized")

    @staticmethod
    def start():
        web.ping()
        active._scheduler.enter_recurring(60, 1, web.ping)
        logging.debug("active scheduler started")

    @staticmethod
    def stop():
        active._scheduler.stop(hard_stop=True)
        logging.debug("active scheduler stopped")
