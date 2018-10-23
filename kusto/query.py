from abc import ABC, abstractmethod

class Query(ABC):
    """Query base class."""
    
    @abstractmethod
    def build(self, **kwargs):
        pass

    @abstractmethod
    def postprocess(self, result):
        pass