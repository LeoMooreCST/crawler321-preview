from data_model import *
from crawler_strategy import *
from extraction_strategy import *
from utils import *
from database import *
'''
    crawler 启动器
'''
class RunCrawler:
    def __init__(
        self,
        crawler_strategy: CrawlerStrategy=None,
        cache: bool=False,
        report: bool=False,
        new_crawl: bool=False,
        **kwargs
    ):
        self.crawler_strategy = crawler_strategy or RequestsCrawlerStrategy()
        self.cache = cache
        self.report = report
        self.new_crawl = new_crawl
        if self.report:
            self.crawler_id = self.get_unique_id() if self.new_crawl else \
            (load_objects("crawler_id") or self.get_unique_id())
    def set_crawler_strategy(self, crawler_strategy: CrawlerStrategy):
        self.crawler_strategy = crawler_strategy
    def set_cache(self, cache: bool):
        self.cache = cache
    def set_report(self, report: bool):
        self.report = report
        if self.report:
            self.crawler_id = self.get_unique_id() if self.new_crawl else \
            (load_objects("crawler_id") or self.get_unique_id())
    def set_new_crawl(self, new_crawl: bool):
        self.new_crawl = new_crawl

    def get_unique_id(self) -> str:
        while True:
            identifier = generate_identifier()
            if not insert_identifier(identifier):
                save_objects("crawler_id", identifier)
                return identifier
    def run(
        self, 
        url: str, 
        proxy: bool=False,
        encoding: str="UTF-8",
        auto_identify: bool=True,
        extraction_strategy: ExtractionStractegy = None,
        **kwargs
    ) -> str:
        try:
            auto = not extraction_strategy and auto_identify
            extraction_strategy = extraction_strategy or NoExtractionStrategy()
            def get_html_strategy():
                if False:
                    html = extraction_strategy.execute(
                        url, proxy, kwargs.get("actions") or None
                    )
                else:
                    html = self.crawler_strategy.crawl(
                        url=url, 
                        proxy=proxy, 
                        encoding=encoding, 
                        actions=kwargs.get("actions") or None
                    )
                if auto:
                    return html, self.get_extraction_strategy(html=html)
                else:
                    return html
            # check cache
            t1 = time.time()
            if auto:
                html, extraction_strategy = get_html_strategy()
            t2 = time.time()
            if self.cache:
                params_str = extraction_strategy.params_to_str()
                strategy_str = extraction_strategy.to_string()
                query_res = query_and_update(
                    self.crawler_id, url, strategy_str, params_str, t2-t1
                )
                if query_res.get("res"):
                    return json.dumps(query_res, indent=4). \
                           encode(encoding).decode('unicode_escape')
            t3 = time.time()
            if not auto:
                html = get_html_strategy()
            extraction_result = extraction_strategy.extract(url=url, html=html)
            html_result = self.process_result(url, html, extraction_result)
            t4 = time.time()
            if self.report:
                params_str = extraction_strategy.params_to_str()
                strategy_str = extraction_strategy.to_string()
                insert_data(
                    self.crawler_id, url, strategy_str, params_str,
                    html_result.model_dump_json(exclude_none=True), 200, t4-t3
                )
            return html_result.model_dump_json(indent=4, exclude_none=True)
        except Exception as e:
            if not hasattr(e, "msg"):
                e.msg = str(e)
            print(e)
        pass
    def get_extraction_strategy(self, html: str) -> ExtractionStractegy:
        soup = html_filter(html=html)
        features = get_web_feature(soup)
        pred_category = pred_web_category(features, "svm")
        if pred_category == "link":
            return PageLinksExtractionStrategy()
        elif pred_category == "text":
            return TextExtractionStrategy()
        elif pred_category == "object":
            return ObjectExtractionStrategy()
        else:
            return NoExtractionStrategy()
    def process_result(self, url:str, html: str, extraction_result: dict):
        meta_result = get_mata_data(html=html)
        return HTMLResult(
            url=url,
            title=meta_result.get('title'),
            keywords=meta_result.get('keywords'),
            description=meta_result.get('description'),
            author=meta_result.get('author'),
            source=meta_result.get('source'),
            res=extraction_result
        )
    def flush_all(self):
        # warn
        delete_data_all()
        pass
    def get_curr_all(self):
        return query_by_identifier(self.crawler_id)
    def flush_curr_all(self):
        delete_by_identifier(self.crawler_id)
    def generate_report(self, path: str=None, id: str=None):
        path = path or "./"
        id = id or self.crawler_id
        df = query_by_identifier(identifier=id)
        # response number
        total_req, success_req, fail_req = len(df), df[df["status"] == 200], df[df["status"] != 200]
        success_rate = len(success_req) / total_req * 100

        # response time
        avg_time = df["time"].mean()
        min_time, max_time = df["time"].min(), df["time"].max()
        num_bins = 10
        time_bins = np.linspace(min_time, max_time, num_bins + 1)

        distributions = [
            df["status"].value_counts(), 
            pd.cut(df["time"], bins=time_bins).value_counts().sort_index(),
            df["strategy"].value_counts(), 
            df["params"].value_counts()
        ]
        column_names = [
            ["状态码", "数量"], 
            ["响应时间区间", "数量"], 
            ["策略", "数量"], 
            ["参数", "数量"]
        ]
        sheet_names = ["状态码分布", "响应时间分布", "策略分布", "参数分布"]

        # Generate report
        report = {
            "总请求数": total_req,
            "请求成功数": len(success_req),
            "请求失败数": len(fail_req),
            "成功率": f"{success_rate: .6f}%",
            "平均响应时间": f"{avg_time: .6f}s",
            "最小响应时间": f"{min_time: .6f}s",
            "最大响应时间": f"{max_time: .6f}s"
        }
        report_df = pd.DataFrame(list(report.items()), columns=["指标", "统计结果"])
        failed_urls_df = df[df["status"] != 200][["url", "status"]]
        report_name = os.path.join(path, "report.xlsx")
        with pd.ExcelWriter(report_name) as writer:
            report_df.to_excel(
                writer, sheet_name="统计报告", index=False
            )
            failed_urls_df.to_excel(
                writer, sheet_name="失败的URL", index=False
            )
            for i in range(len(distributions)):
                dis_df =  pd.DataFrame(
                    distributions[i].items(), columns=column_names[i]
                )
                dis_df.to_excel(
                    writer, sheet_name=sheet_names[i], index=False
                )
                

        