from abc import ABC, abstractmethod

class BaseExtraction(ABC):
    '''
        Base models for strategies
    '''
    @abstractmethod
    def extract(self, url: str, html: str, **kwargs):
        pass
    @abstractmethod
    def next_run(self, url: str, res):
        pass
    @abstractmethod
    def to_string(self) -> str:
        pass
    
    def params_to_str(self) -> str:
        params = vars(self)
        # 过滤掉值为None的参数
        filtered_params = {k: v for k, v in params.items() if v is not None}
        # 将参数和值转换为字符串
        params_str = ",".join(f"{key}={str(value)}" for key, value in filtered_params.items())
        return params_str