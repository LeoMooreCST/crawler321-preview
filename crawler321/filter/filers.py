import re
import time
from typing import Optional
from crawler321.config import FilterContext, CrawlerResponse, ContentType, HTMLResult
from crawler321.extraction import BaseExtraction
from .interceptors import InterceptingFilter
from crawler321.utils import is_media_type, html_filter, get_web_feature, pred_web_category, get_mata_data
from crawler321.extraction import *
from crawler321._legacy.database import query_and_update, insert_data
import hashlib
import json
from crawler321.utils import html_filter, get_web_feature, pred_web_category
"""验证过滤器"""
class ValidationFilter(InterceptingFilter):
    # async
    def before_request(self, context: FilterContext) -> Optional[CrawlerResponse]:
        self.logger.info(f"验证请求: {context.request.url}")
        # URL合法性验证
        if not self._is_valid_url(context.request.url):
            return CrawlerResponse(
                content=None,
                status_code=400,
                content_type=ContentType.TEXT,
                success=False,
                error=f"无效的URL格式: {context.request.url}"
            )
        # HTTP方法验证
        if context.request.method.upper() not in ["GET", "POST", "PUT", "DELETE", "HEAD"]:
            return CrawlerResponse(
                content=None,
                status_code=400,
                content_type=ContentType.TEXT,
                success=False,
                error=f"不支持的HTTP方法: {context.request.method}"
            )
        return None
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(pattern.match(url))

"""策略选择过滤器"""
class ExtractionFilter(InterceptingFilter):
    # async
    # 识别策略类型做缓存
    def before_request(self, context: FilterContext) -> Optional[CrawlerResponse]:
        if context.request.auto:
            context.data['cache_params'] = 'auto'
        else:
            if context.request.extraction_strategy is None:
                context.request.extraction_strategy = DefaultExtraction()
            context.data['cache_params'] = context.request.extraction_strategy.to_string()  + \
            context.request.extraction_strategy.params_to_str()
        return None
    # async
    def after_request(self, context: FilterContext) -> CrawlerResponse:
        if not context.response.success:
            return context.response
        # 自动识别策略
        if context.request.auto:
            soup = html_filter(context.response.content)
            features = get_web_feature(soup)
            pred = pred_web_category(features, "svm")
            if pred == "link":
                context.request.extraction_strategy = PageLinkExtraction()
            elif pred == "text":
                context.request.extraction_strategy = TextExtraction()
            elif pred == "object":
                context.request.extraction_strategy = ObjectExtraction()
            else:
                context.request.extraction_strategy = DefaultExtraction()
        return self._parse_content(context)
    def _parse_content(self, context: FilterContext) -> CrawlerResponse:
        response = context.response
        try:
            meta_result = get_mata_data(response.content)
            html_result = HTMLResult(
                url=context.request.url,
                title=meta_result.get('title'),
                keywords=meta_result.get('keywords'),
                description=meta_result.get('description'),
                author=meta_result.get('author'),
                source=meta_result.get('source'),
                res=context.request.extraction_strategy.extract(
                    context.request.url, response.content
                )
            )
            # 将HTML结果添加到响应
            response.metadata['html_result'] = html_result
        except Exception as e:
            self.logger.error(f"结果构建失败: {str(e)}")
        return response

"""缓存过滤器"""
class CacheFilter(InterceptingFilter):
    def __init__(
            self, 
            db,
            use_cache: bool, 
            use_store: bool, 
            ttl: int = 3600, 
            name: str = None
        ):
        super().__init__(name)
        self.db = db
        self.use_cache = use_cache
        self.use_store = use_store
        self.ttl = ttl
    # async
    def before_request(self, context: FilterContext) -> Optional[CrawlerResponse]:
        if not self.use_cache:
            return None
        self.logger.info(f"检查缓存: {context.request.url}")
        cache_key = self._build_cache_key(
            context.request.url, context.data.get("cache_params", "")
        )
        cached = self.db.get_cache(cache_key)
        if cached:
            self.logger.info(f"缓存命中: {context.request.url}")
            context.data['cache_hit'] = True
            context.data['cache_key'] = cache_key
            cached_result = HTMLResult(
                url=cached['url'],
                title=cached['title'],
                keywords=cached['keywords'],
                description=cached['description'],
                author=cached['author'],
                source=['source'],
                res=json.loads(cached['content'])
            )
            response = CrawlerResponse(
                status_code=200,
                success=True,
                metadata={'html_result': cached_result}
            )
            return response
        context.data['cache_hit'] = False
        return None
    def after_request(self, context: FilterContext) -> CrawlerResponse:
        if context.response.success and self.use_store:
            cache_key = self._build_cache_key(
                context.request.url, context.data.get("cache_params", "")
            )
            html_result = context.response.metadata.get("html_result")
            self.db.set_cache(cache_key, html_result)
        return context.response
    def _build_cache_key(self, url, params):
        """构建缓存键"""
        key_data = {
            'url': url,
            'params': params
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

class ReportingFilter(InterceptingFilter):
    def __init__(self, db, crawler_id: str, name = None):
        super().__init__(name)
        self.db = db
        self.crawler_id = crawler_id
    def after_request(self, context: FilterContext) -> CrawlerResponse:
        self.insert_crawl_result(
            {
                "crawler_id": self.crawler_id,
                "url": context.request.url,
                "method": context.request.method,
                "status_code": context.response.status_code,
                "strategy": context.request.extraction_strategy.to_string(),
                "params": context.request.extraction_strategy.params_to_str(),
                "elapsed_time": time.time() - context.response.elapsed_time,
                "success": context.response.success,
                "error_message": context.response.error,
                "cache_hit": context.data.get("cache_hit")
            }
        )
        return context.response