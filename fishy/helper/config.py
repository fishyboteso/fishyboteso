"""
config.py
Saves configuration in file as json file
"""
import json
import os

# path to save the configuration file
filename = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"], "Documents", "fishy_config.json")


class Config:

    def __init__(self):
        """
        cache the configuration in a dict for faster access,
        if file is not found initialize the dict
        """
        self.config_dict = json.loads(open(filename).read()) if os.path.exists(filename) else dict()

    def get(self, key, default=None):
        """
        gets a value from  configuration,
        if it is not found, return the default configuration
        :param key: key of the config
        :param default: default value to return if key is not found
        :return: config value
        """
        return self.config_dict[key] if key in self.config_dict else default

    def set(self, key, value, save=True):
        """
        saves the configuration is cache (and saves it in file if needed)
        :param key: key to save
        :param value: value to save
        :param save: False if don't want to save right away
        """
        self.config_dict[key] = value
        if save:
            self.save_config()

    def delete(self, key):
        """
        deletes a key from config
        :param key: key to delete
        """
        del self.config_dict[key]
        self.save_config()

    def save_config(self):
        """
        save the cache to the file
        """
        with open(filename, 'w') as f:
            f.write(json.dumps(self.config_dict))

