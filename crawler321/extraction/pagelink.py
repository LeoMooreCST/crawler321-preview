from .base import BaseExtraction
from crawler321.utils import *

'''
    提取一个页面的有效链接(如某个网站主页, 同一页面有多个相似的列表链接)

    :param min_len: 有效链接的最小划分数目, 默认值为8
    :param auto_filter: 是否自动过滤, 如果是则返回自动过滤后的链接[], 否则返回所有clustering结果供用户筛选
    :param sequential:  是否同级连续爬取, 如果是则爬取[下页, 下页, 后页]所有可能的链接

    :return A lists of the urls
'''
class PageLinkExtraction(BaseExtraction):
    def __init__(
        self, 
        min_len: int=8, 
        auto_filter: bool=True, 
        sequential: bool=False
    ):
        self.min_len = min_len
        self.auto_filter = auto_filter
        self.sequential = sequential
        self.common_urls = {}    # 这里可以做cache的为了有多次寻找
    def extract(self, url: str, html: str, **kwargs):
        self.cluster_res = {
            "urls": {},
            "titles": {}
        }
        self.crawler = kwargs.get("crawler")
        self.proxy = kwargs.get("proxy")
        self.encoding = kwargs.get("encoding")
        soup = html_filter(html=html)
        alinks = get_a_links(soup, url)
        # 进一步优化：
        next_page_url = get_next_pagination(
            soup=get_pretty_soup(html), 
            base_url=url
        )
        if next_page_url and not self.common_urls:   # 注意需要修正一下
            html_next, code= self.crawler.crawl(
                url=next_page_url,
                proxy=self.proxy,
                encoding=self.encoding
            )
            soup_next = html_filter(html=html_next)
            alinks_next = get_a_links(soup_next, next_page_url)
            self.common_urls = get_common_urls(alinks, alinks_next)
            if self.common_urls:
                alinks = get_diff_urls(alinks, self.common_urls)
        formalized_urls = formalize_urls(alinks)
        clusters = clustering_urls(formalized_urls, self.min_len)
        self.handle_clustering(clusters, formalized_urls)
        self.next_run(next_page_url, "")
        return self.cluster_res
    def next_run(self, url: str, res):
        while url and self.sequential:
            html_next, code= self.crawler.crawl(
                url=url,
                proxy=self.proxy,
                encoding=self.encoding
            )
            soup_next = html_filter(html=html_next)
            alinks_next = get_a_links(soup_next, url)
            if self.common_urls:
                alinks_next = get_diff_urls(alinks_next, self.common_urls)
            formalized_urls = formalize_urls(alinks_next)
            clusters = clustering_urls(formalized_urls, self.min_len)
            self.handle_clustering(clusters, formalized_urls)
            url = get_next_pagination(
                get_pretty_soup(html_next), 
                base_url=url
            )
    def handle_clustering(self, clusters, urls):
        # 获取所有唯一的类标签
        unique_labels = np.unique(clusters)
        if len(unique_labels) == 1:
            cluster_urls = np.array(urls)[clusters == unique_labels[0]]
            urls_list = [url['full_url'] for url in cluster_urls]
            url_contents = [url['content'] for url in cluster_urls]
            self.cluster_res["urls"][len(self.cluster_res["urls"])] = urls_list
            self.cluster_res["titles"][len(self.cluster_res["titles"])] = url_contents
        elif self.auto_filter:
            # 初始化一个字典来统计每个类的数量
            class_counts = { label: len(np.where(clusters == label)[0]) 
                            for label in unique_labels if label != -1 }
            most_common_class = Counter(class_counts).most_common(1)[0][0]
            # 获取数量最多的类的元素列表
            cluster_urls = np.array(urls)[clusters == most_common_class]
            urls_list = [url['full_url'] for url in cluster_urls]
            url_contents = [url['content'] for url in cluster_urls]
            self.cluster_res["urls"][len(self.cluster_res["urls"])] = urls_list
            self.cluster_res["titles"][len(self.cluster_res["titles"])] = url_contents
        else:
            # 将各个元素放入对应类的列表中
            for label in unique_labels:
                if label == -1:
                    continue
                cluster_urls = np.array(urls)[clusters == label]
                urls_list = [url['full_url'] for url in cluster_urls]
                url_contents = [url['content'] for url in cluster_urls]
                self.cluster_res["urls"][len(self.cluster_res["urls"])] = urls_list
                self.cluster_res["titles"][len(self.cluster_res["titles"])] = url_contents
    def to_string(self) -> str:
        return "PageLinks"
    def params_to_str(self) -> str:
        params = vars(self)
        # 过滤掉值为None的参数
        filtered_params = {k: v for k, v in params.items() if v is not None and k != "common_urls"}
        # 将参数和值转换为字符串
        params_str = ",".join(f"{key}={str(value)}" for key, value in filtered_params.items())
        return params_str
        # return super().params_to_str()
