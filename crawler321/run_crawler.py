import uuid
from .config import RunConfig, FilterContext, CrawlerResponse
from .crawler_strategy import RequestsCrawlerStrategy
from .filter import FilterChainManager
import logging
logger = logging.getLogger(__name__)
class RunCrawler:
    def __init__(
        self,
        crawler_strategy=None,
        db=None,
        cache_enabled: bool = False,
        store_enabled: bool = False,
        report_enabled: bool = False,
        crawler_id: str = None,
        **kwargs
    ):
        self.crawler_strategy = crawler_strategy or RequestsCrawlerStrategy()
        self.db = db
        self.cache_enabled = cache_enabled
        self.store_enabled = store_enabled
        self.report_enabled = report_enabled
        self.crawler_id = crawler_id or self._generate_crawler_id()
        self.filter_manager = FilterChainManager()
        self._build_filter_chain()
    
    def _generate_crawler_id(self) -> str:
        if not self.db:
            return ""
        id = self.db.get_crawler_id()
        if not id:
            id = f"crawler_{uuid.uuid4().hex[:8]}"
            self.db.update_crawler_id(id)
        return id
    def get_crawler_id(self) -> str:
        return self.crawler_id
    def _build_filter_chain(self):
        self.filter_manager.build_custom_chain(
            crawler_strategy=self.crawler_strategy,
            db=self.db,
            crawler_id=self.crawler_id,
            use_cache=self.cache_enabled,
            use_store=self.store_enabled,
            use_report=self.report_enabled
        )
    
    def run(
        self,
        config: RunConfig = None,
        **kwargs
    ) -> dict:
        try:
            context = FilterContext(config)
            response: CrawlerResponse = self.filter_manager.run_chain(context)
            result = {
                "success": response.success,
                "status_code": response.status_code,
                "data": response.metadata.get("html_result") 
                        if response.success 
                        else response.error
            }
            return result
        except Exception as e:
            error_result = {
                "url": config.url,
                "success": False,
                "data": f"系统错误: {str(e)}"
            }
            # return json.dumps(error_result, indent=4, ensure_ascii=False)
            return error_result
