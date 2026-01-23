from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from .extraction import BaseExtraction

class UrlResults(BaseModel):
    page_num: int
    urls: list

class HTMLResult(BaseModel):
    url: str
    title: Optional[str] = None
    keywords: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    res: Optional[dict] = None

class ContentType(Enum):
    HTML = "html"
    JSON = "json"
    MEDIA = "media"
    TEXT = "text"

@dataclass
class RunConfig:
    '''爬虫请求对象'''
    url: str
    method: str = "GET"
    proxy: bool = False
    encoding: str = "UTF-8"
    auto: bool = False
    extraction_strategy: BaseExtraction = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30
    retry_times: int = 5
    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if self.headers is None:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 '
                  'Safari/537.36',
                "Connection": "close"
            }
@dataclass
class CrawlerResponse:
    """爬虫响应对象"""
    content: Any
    status_code: int
    content_type: ContentType
    success: bool = True
    error: Optional[str] = None
    elapsed_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class FilterContext:
    """过滤器上下文"""
    request: RunConfig
    response: Optional[CrawlerResponse] = None
    should_continue: bool = True
    error: Optional[Exception] = None
    data: Dict[str, Any] = field(default_factory=dict)
    
    def set_response(self, response: CrawlerResponse):
        """设置响应"""
        self.response = response
    
    def set_error(self, error: Exception):
        """设置错误"""
        self.error = error
        self.should_continue = False