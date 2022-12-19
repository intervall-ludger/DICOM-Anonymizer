from abc import ABC, abstractmethod
from .logger import logger

# Abstract class for mode configuration
class AbstractModeConfiguration(ABC):

    # Method to change the value of a given key to either True or False
    def change_bool(self, key: str):
        if key in self.change_true_keys():
            return True
        if key in self.change_false_keys():
            return False
        logger.info("Change key ")
        return True

    # Method to return a list of keys that should be changed to True
    @abstractmethod
    def change_true_keys(self):
        pass

    # Method to return a list of keys that should be changed to False
    @abstractmethod
    def change_false_keys(self):
        pass

# Class for hard anonymization mode configuration
class HardAnonymize(AbstractModeConfiguration, ABC):

    # Return list of keys that should be changed to True
    def change_true_keys(self):
        return ['ImageType', 'Pixel', 'SliceThickness', 'SliceLocation', 'Rows', 'Columns', 'BitsAllocated',
                'BitsStored', 'WindowCenter', 'WindowWidth', 'HighBit']

    # Return empty list of keys that should be changed to False
    def change_false_keys(self):
        return []

# Class for only critical anonymization mode configuration
class OnlyCriticalAnonymize(AbstractModeConfiguration, ABC):

    # Return list of keys that should be changed to True
    def change_true_keys(self):
        return ['ImageType', 'Pixel', 'SliceThickness', 'SliceLocation', 'Rows', 'Columns', 'BitsAllocated',
                'BitsStored', 'WindowCenter', 'WindowWidth', 'HighBit']

    # Return empty list of keys that should be changed to False
    def change_false_keys(self):
        return []
