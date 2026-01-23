from .base import BaseLLMAdpater
from crawler321.llm.config import SparkConfig
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

class SparkLLMAdapter(BaseLLMAdpater):
    def __init__(self, config: SparkConfig):
        self._cfg = {
            "spark_app_id": config.app_id,
            "spark_api_key": config.api_key,
            "spark_api_secret": config.api_secret,
            "spark_api_url": config.spark_api_url,
            "spark_llm_domain": config.spark_llm_domain,
            "streaming": config.streaming,
            "temperature": config.temperature,
        }
    def generate(self, promt, max_tokens):
        self._cfg["max_tokens"] = max_tokens
        llm = ChatSparkLLM(**self._cfg)
        message = llm.generate([ChatMessage(role="user", content=promt)])
        handler = ChunkPrintHandler()
        res = llm.generate([message], callbacks=[handler])
        return res.generations[0][0].text