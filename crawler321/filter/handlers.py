from .interceptors import FilterHandler
from crawler321.config import CrawlerResponse, ContentType
import time

class CrawlerHandler(FilterHandler):
    """爬虫核心处理器"""
    
    def __init__(self, crawler_strategy):
        self.crawler_strategy = crawler_strategy
    # async
    def handle(self, request, next_handler=None):
        """执行实际的爬取操作"""
        try:
            # 使用爬虫策略获取内容
            content, status_code = self.crawler_strategy.crawl(
                url=request.url,
                method=request.method,
                params=request.params,
                data=request.data,
                proxy=request.proxy,
                encoding=request.encoding,
                timeout=request.timeout
            )
            return CrawlerResponse(
                content=content,
                status_code=status_code,
                content_type=ContentType.HTML
            )
        except Exception as e:
            return CrawlerResponse(
                content=None,
                status_code=500,
                content_type=ContentType.TEXT,
                success=False,
                error=str(e)
            )