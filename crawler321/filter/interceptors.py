from abc import ABC, abstractmethod
from typing import Optional, Callable, List
from crawler321.constant import StatusCode
import logging, time
from crawler321.config import FilterContext, CrawlerResponse, ContentType

logger = logging.getLogger(__name__)

class FilterHandler:
    """过滤器处理接口"""
    @abstractmethod
    def handle(self, request, next_handler: Optional[Callable]): # async
        pass

class InterceptingFilter(ABC):
    """拦截过滤器抽象基类"""
    def __init__(self, name: str = None):
        self.name = name
        self.logger = logging.getLogger(f"filter.{self.name}")
    def before_request(self, context: FilterContext) -> Optional[CrawlerResponse]: # async
        """请求前处理, 返回None表示继续"""
        return None
    # # async
    def after_request(self, context: FilterContext) -> CrawlerResponse:
        """请求后处理"""
        return context.response

class FilterChain:
    """过滤器链"""
    def __init__(self, filters: List[InterceptingFilter], handler: FilterHandler):
        self.filters = filters
        self.handler = handler
    def add_filter(self, filter: InterceptingFilter):
        self.filters.append(filter)
    # async
    def execute(self, context: FilterContext) -> CrawlerResponse:
        """执行过滤器链"""
        try:
            start_time = time.time()
            for filter in self.filters:
                filter_response = filter.before_request(context)
                # 被cache拦截
                if filter_response is not None:
                    filter_response.elapsed_time = time.time() - start_time
                    return filter_response
            # 执行主处理器
            response = self.handler.handle(context.request, None) # await    
            context.set_response(response)
            response.elapsed_time = start_time
            # 执行所有过滤器的after()
            for filter in self.filters:
                context.response = filter.after_request(context) # await
            return context.response 
        except Exception as e:
            logger.error(f"过滤器链执行失败: {str(e)}", exc_info=True)
            context.set_error(e)
            return CrawlerResponse(
                content=None,
                status_code=StatusCode.INTERNAL_SERVER_ERROR,
                content_type=ContentType.TEXT,
                success=False,
                error=str(e)
            )