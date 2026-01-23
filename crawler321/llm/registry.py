from .adpater import *
from .config import *
class LLMAdapterRegistry:
    """
    Application-scope registry
    - 只负责：Config -> Adapter 的映射
    - 不保存运行态状态
    """
    def create_adapter(self, config):
        if isinstance(config, SparkConfig):
            return SparkLLMAdapter(config)
        if isinstance(config, DeepSeekConfig):
            return DeepSeekLLMAdapter(config)
        raise NotImplementedError(
            f"No adapter registered for config type: {type(config)}"
        )


# ==============================
# 模块级单例（推荐）
# ==============================

adapter_registry = LLMAdapterRegistry()
