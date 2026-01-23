from crawler321.crawler_strategy import SeleniumCrawlerStrategy
from .base import BaseExtraction
from lxml import etree
from crawler321.utils import formalize_xpath
class XPathExtraction(BaseExtraction):
    '''
        最好做一下缓存, 需要chrome支持
    '''
    def __init__(
        self, 
        keys: list=None, 
        words: list=None
    ):
        if not words:
            raise ValueError("[Error]❌ Please input the unique keys in XPathExtractionStrategy()!")
        self.driver = SeleniumCrawlerStrategy()
        self.words = words
        self.keys = keys or [id for id in range(len(words))]
        self.xpaths = None
    def execute(
        self, 
        url: str, 
        proxy: bool=False, 
        actions: list=[]
    ):
        html = self.driver.crawl(
            url=url, 
            proxy=proxy, 
            actions=actions
        )
        return html
    def extract(self, url: str, html: str, **kwargs):
        # 注意py3.8及以上才能使用
        if self.xpaths is None:
            self.xpaths = [
                formalize_xpath(elements[0]) if elements else ""
                for word in self.words
                if (elements := self.driver.find_element_xpath(keyword=word))
            ]
        e = etree.HTML(html)
        return {
            key: ([text for s in e.xpath(xpath) if (text := s.text.strip())] if xpath else [])
            for key, xpath in zip(self.keys, self.xpaths)
        }
    def next_run(self, url: str, res):
        return super().next_run(url, res)
    def to_string(self) -> str:
        return "XPath"
    def params_to_str(self) -> str:
        return super().params_to_str()