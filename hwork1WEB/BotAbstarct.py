from AddressBook import *
from abc import ABC, abstractmethod
from Bot import Bot

class Abstract(ABC):
    @abstractmethod
    def handle(self, action):
        bot = Bot()
        bot.handle(action)
