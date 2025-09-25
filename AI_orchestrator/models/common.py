from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def generateResponse(self, message, **kwargs):
        pass

    @abstractmethod
    def getModelInfo(self):
        pass