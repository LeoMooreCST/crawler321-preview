from typing import List
from .interceptors import FilterChain, InterceptingFilter
from .handlers import CrawlerHandler
from .filers import *

class FilterChainManager:
    def __init__(self):
        self.chain: FilterChain = None
    def setFilter(self, filter: InterceptingFilter):
        self.chain.add_filter(filter)
    def run_chain(self, context):
        return self.chain.execute(context)
    def build_custom_chain(
        self,
        crawler_strategy,
        db = None,
        crawler_id: str = None, 
        use_cache: bool = False, 
        use_store: bool = False,
        use_report: bool = False
    ) -> FilterChain:
        filters: List[InterceptingFilter] = []
        filters.append(ValidationFilter())
        filters.append(ExtractionFilter())
        if db and (use_cache or use_store):
            filters.append(CacheFilter(db=db, use_cache=use_cache, use_store=use_store))
        if use_report and db:
            filters.append(ReportingFilter(db=db, crawler_id=crawler_id))
        handler = CrawlerHandler(crawler_strategy)
        self.chain = FilterChain(filters, handler)