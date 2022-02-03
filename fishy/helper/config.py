"""
config.py
Saves configuration in file as json file
"""
import json
import logging
import os
# path to save the configuration file
from typing import Optional

from event_scheduler import EventScheduler


def filename():
    from fishy.helper.helper import get_documents
    name = "fishy_config.json"
    _filename = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], "Documents", name)
    if os.path.exists(_filename):
        return _filename

    return os.path.join(get_documents(), name)


temp_file = os.path.join(os.environ["TEMP"], "fishy_config.BAK")


class Config:

    def __init__(self):
        self._config_dict: Optional[dict] = None
        self._scheduler: Optional[EventScheduler] = None

    def __getitem__(self, item):
        return self._config_dict.get(item)

    def __setitem__(self, key, value):
        self._config_dict[key] = value

    def __delitem__(self, key):
        del self._config_dict[key]

    def initialize(self):
        self._scheduler = EventScheduler()
        if os.path.exists(filename()):

            try:
                self._config_dict = json.loads(open(filename()).read())
            except json.JSONDecodeError:
                try:
                    logging.warning("Config file got corrupted, trying to restore backup")
                    self._config_dict = json.loads(open(temp_file).read())
                    self.save_config()
                except (FileNotFoundError, json.JSONDecodeError):
                    logging.warning("couldn't restore, creating new")
                    os.remove(filename())
                    self._config_dict = dict()

        else:
            self._config_dict = dict()
        logging.debug("config initialized")

    def start_backup_scheduler(self):
        self._create_backup()
        self._scheduler.start()
        self._scheduler.enter_recurring(5 * 60, 1, self._create_backup)
        logging.debug("scheduler started")

    def stop(self):
        self._scheduler.stop(True)
        logging.debug("config stopped")

    def _create_backup(self):
        with open(temp_file, 'w') as f:
            f.write(json.dumps(self._config_dict))
        logging.debug("created backup")

    def _sort_dict(self):
        tmpdict = dict()
        for key in sorted(self._config_dict.keys()):
            tmpdict[key] = self._config_dict[key]
        self._config_dict = tmpdict

    def save_config(self):
        """
        save the cache to the file
        """
        self._sort_dict()
        with open(filename(), 'w') as f:
            f.write(json.dumps(self._config_dict))


# noinspection PyPep8Naming
class config:
    _instance = None

    @staticmethod
    def init():
        if not config._instance:
            config._instance = Config()
            config._instance.initialize()

    @staticmethod
    def start_backup_scheduler():
        config._instance.start_backup_scheduler()

    @staticmethod
    def stop():
        config._instance.stop()

    @staticmethod
    def get(key, default=None):
        """
        gets a value from  configuration,
        if it is not found, return the default configuration
        :param key: key of the config
        :param default: default value to return if key is not found
        :return: config value
        """
        return default if config._instance is None or config._instance[key] is None else config._instance[key]

    @staticmethod
    def set(key, value, save=True):
        """
        saves the configuration is cache (and saves it in file if needed)
        :param key: key to save
        :param value: value to save
        :param save: False if don't want to save right away
        """
        if config._instance is None:
            return

        config._instance[key] = value
        if save:
            config.save_config()

    @staticmethod
    def delete(key):
        """
        deletes a key from config
        :param key: key to delete
        """
        try:
            del config._instance[key]
            config.save_config()
        except KeyError:
            pass

    @staticmethod
    def save_config():
        if config._instance is None:
            return
        config._instance.save_config()
