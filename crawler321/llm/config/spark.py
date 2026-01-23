from dataclasses import dataclass

@dataclass
class SparkConfig:
    app_id: str
    api_key: str
    api_secret: str
    model: str = "Spark/Lite",
    streaming: bool = False,
    temperature: float = 0.2
    def __post_init__(self):
        if not all([self.app_id, self.api_key, self.api_secret]):
            raise ValueError("⚠ SparkConfig incomplete")
        elif SPARK_CONFIG.get(self.model) is None:
            raise ValueError("❌ Spark model name incorrect!")
        else:
            self.spark_api_url = SPARK_CONFIG[self.model].get("SPARKAI_URL")
            self.spark_llm_domain = SPARK_CONFIG[self.model].get("SPARKAI_DOMAIN")

SPARK_CONFIG = {
    "Spark/Lite": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v1.1/chat",
        "SPARKAI_DOMAIN": "general"
        },
    "Spark/V2.0": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v2.1/chat",
        "SPARKAI_DOMAIN": "generalv2"
        },
    "Spark/Pro": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v3.1/chat",
        "SPARKAI_DOMAIN": "generalv3"
        },
    "Spark/Pro-128K": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/chat/pro-128k",
        "SPARKAI_DOMAIN": "pro-128k"
        },
    "Spark/Max": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v3.5/chat",
        "SPARKAI_DOMAIN": "generalv3.5"
        },
    "Spark/4.0Ultra": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v4.0/chat",
        "SPARKAI_DOMAIN": "4.0Ultra"
        }
}