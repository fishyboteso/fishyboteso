from abc import ABC, abstractmethod
from enum import Enum


class FullAutoMode(Enum):
    Player = 0
    Recorder = 1


class IMode(ABC):

    @abstractmethod
    def run(self):
        ...
