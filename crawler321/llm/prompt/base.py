from abc import ABC, abstractmethod

class BasePrompt(ABC):
    name: str
    @abstractmethod
    def build(self, content: str) -> str:
        pass