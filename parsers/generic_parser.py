from abc import ABCMeta, abstractmethod

class GenericParser:
    """
    Abstract class for parsing financial transactions from different
    institutions
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse_file(self): pass