from dataclasses import dataclass

@dataclass
class DeepSeekConfig:
    api_key: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    base_url: str = "https://api.deepseek.com"
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("⚠ DeepSeekConfig missing api_key")
    