from .run_crawler import RunCrawler
from .crawler_strategy import RequestsCrawlerStrategy, SeleniumCrawlerStrategy

from .config import (
    RunConfig
)
from crawler321.service import (
    CrawlerDatabase,
    CrawlerReport
)

from .SeleniumCommand import (
    SeleniumCommand,
    DefaultCMD,
    RefreshCMD,
    BackCMD,
    ForwardCMD,
    ClickCMD,
    InputCMD,
    UploadCMD,
    ScrollCMD,
    JsCMD,
    QuitCMD
)

from .proxy_strategy import (
    JuLiangAPI,
    JiGuangAPI,
    PinYiAPI,

    ProxyAdapter,
    JuLiangAdapter,
    JiGuangAdapter,
    PinYiAdapter,
    NoProxyAdapter
)

from .llm import (
    SparkConfig,
    DeepSeekConfig,
    SparkLLMAdapter,
    DeepSeekLLMAdapter,
    BasePrompt,
    SimplePrompt
)

from .extraction import (
    BaseExtraction,
    DefaultExtraction,
    LLMExtraction,
    MediaExtraction,
    ObjectExtraction,
    PageLinkExtraction,
    TextExtraction,
    # XPathExtraction
)

__all__ = [
    # 运行爬虫相关
    'RunCrawler',
    
    # 爬虫策略
    'RequestsCrawlerStrategy',
    'SeleniumCrawlerStrategy',
    
    # 配置
    'RunConfig',
    
    # 服务
    'CrawlerDatabase',
    'CrawlerReport',
    
    # 提取策略
    'BaseExtraction',
    'DefaultExtraction',
    'LLMExtraction',
    'MediaExtraction',
    'ObjectExtraction',
    'PageLinkExtraction',
    'TextExtraction',
    # 'XPathExtraction',  # 注释掉了
    
    # Selenium命令
    'SeleniumCommand',
    'DefaultCMD',
    'RefreshCMD',
    'BackCMD',
    'ForwardCMD',
    'ClickCMD',
    'InputCMD',
    'UploadCMD',
    'ScrollCMD',
    'JsCMD',
    'QuitCMD',
    
    # 代理策略接口
    'JuLiangAPI',
    'JiGuangAPI',
    'PinYiAPI',
    
    # 代理适配器
    'ProxyAdapter',
    'JuLiangAdapter',
    'JiGuangAdapter',
    'PinYiAdapter',
    'NoProxyAdapter',
    
    # LLM配置
    'SparkConfig',
    'DeepSeekConfig',
    
    # LLM适配器
    'SparkLLMAdapter',
    'DeepSeekLLMAdapter',
    
    # 提示词
    'BasePrompt',
    'SimplePrompt'
]