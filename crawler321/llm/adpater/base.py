from abc import abstractmethod

class BaseLLMAdpater:
    @abstractmethod
    def generate(self, promt: str, max_tokens: int) -> str:
        pass