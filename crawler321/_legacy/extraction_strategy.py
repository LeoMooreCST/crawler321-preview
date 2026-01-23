from utils import *
from constant import *
from crawler321._legacy.action import SeleniumAction
from crawler_strategy import SeleniumCrawlerStrategy
from crawler321.config import *
from lxml import etree
from typing import Union
from collections import Counter
from urllib.parse import urlparse
from abc import ABC, abstractmethod
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

class ExtractionStractegy(ABC):
    '''
        Base models for strategies
    '''
    @abstractmethod
    def extract(self, url: str, html: str, **kwargs):
        pass
    @abstractmethod
    def next_run(self, url: str, res):
        pass
    @abstractmethod
    def to_string(self) -> str:
        pass
    
    def params_to_str(self) -> str:
        params = vars(self)
        # 过滤掉值为None的参数
        filtered_params = {k: v for k, v in params.items() if v is not None}
        # 将参数和值转换为字符串
        params_str = ",".join(f"{key}={str(value)}" for key, value in filtered_params.items())
        return params_str

'''
    直接返回获取的网页内容

    :return the str of the raw_content
'''
class NoExtractionStrategy(ExtractionStractegy):
    def __init__(
        self, 
        xpaths: Union[str, list]=None, 
        content_type: str="text"
    ):
        self.xpaths = [xpaths] if isinstance(xpaths, str) else xpaths
        self.content_type = content_type
    def extract(self, url: str, html: str, **kwargs):
        if self.xpaths:
            return self.next_run(url, html)
        content = extract_raw_html(html=html) if self.content_type == "text" else html
        length = len(content)
        return formalize_result(TextResult(length=length,content=content))
    def next_run(self, url: str, res):
        e = etree.HTML(res)
        results = {i: e.xpath(xpath) for i, xpath in enumerate(self.xpaths)}
        return results
    def to_string(self) -> str:
        return "No"
    def params_to_str(self) -> str:
        return super().params_to_str()
        

'''
    提取一个页面的有效链接(如某个网站主页, 同一页面有多个相似的列表链接)

    :param min_len: 有效链接的最小划分数目, 默认值为8
    :param auto_filter: 是否自动过滤, 如果是则返回自动过滤后的链接[], 否则返回所有clustering结果供用户筛选
    :param sequential:  是否同级连续爬取, 如果是则爬取[下页, 下页, 后页]所有可能的链接

    :return A lists of the urls
'''
class PageLinksExtractionStrategy(ExtractionStractegy):
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

'''
    提取一个页面的核心内容, 比如新闻网站, 可以使用自定义模型进行提取

    :param model: 提取模型
 
    :return ...
'''
class TextExtractionStrategy(ExtractionStractegy):
    def __init__(self, model: str=None):
        self.model = model or "local"
    def extract(self, url: str, html: str, **kwargs):
        soup = html_filter(html=html)
        return self.next_run(url=url, res=soup)
    def next_run(self, url: str, res):
        contents = ""
        if self.model == "local":
            main_contents = extract_main_content(soup=res)
            contents = ''.join(remove_low_entropy_node(contents=main_contents))
        elif self.model == "your_path_for_model":
            # Extension
            pass
        return formalize_result(
            TextResult(length=len(contents),content=contents)
        )
    def to_string(self) -> str:
        return "Text"
    def params_to_str(self) -> str:
        return super().params_to_str()

'''
    键值-实体提取模型: 适用于网页中存在"key: value"且为核心内容

    :param model: 提取模型, 默认为local      opt
    :param objects: 需要保留的对象 -> list[] opt
    :return ...
'''
class ObjectExtractionStrategy(ExtractionStractegy):
    def __init__(
        self, 
        model: str=None, 
        objects: list=None
    ):
        self.model = model or "local"
        self.objects = objects
    def extract(self, url: str, html: str, **kwargs):
        soup = html_filter(html=html)
        objects = []
        if self.model == "local":
            encode_texts = html_object_encoding(soup=soup)
            # print("[Logger]🍎 编码后的内容为: ", encode_texts)
            objects = extract_object_pairs(encoded_text=encode_texts)
        elif self.model == "your_path_for_model":
            # Extension
            pass
        return self.next_run(url=url, res=objects)
    def next_run(self, url: str, res):
        if not self.objects:
            return {i: item for i, item in enumerate(res)}
        # 提取包含所需键的字典
        filtered_items = [
            {key: item[key] for key in self.objects if key in item}
            for item in res]
        # 过滤掉空字典
        objects = [obj for obj in filtered_items if obj]
        return {i: item for i, item in enumerate(objects)}
    def to_string(self) -> str:
        return "Object"
    def params_to_str(self) -> str:
        return super().params_to_str()

class XPathExtractionStrategy(ExtractionStractegy):
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
        actions: SeleniumAction=None
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

'''
    星火大模型用作示例,其他模型请自己添加接口 侵删
    使用前请详细阅读文档
    星火:   参考文档: https://www.xfyun.cn/doc/spark/Web.html#%E5%BF%AB%E9%80%9F%E8%B0%83%E7%94%A8%E9%9B%86%E6%88%90%E6%98%9F%E7%81%AB%E8%AE%A4%E7%9F%A5%E5%A4%A7%E6%A8%A1%E5%9E%8B%EF%BC%88python%E7%A4%BA%E4%BE%8B%EF%BC%89
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
        max_tokens= 300,
        temperature=0.1
    )
'''
class LLMExtractionStrategy(ExtractionStractegy):
    def __init__(
        self, 
        model: str="Spark/Lite", 
        max_tokens: int=500, 
        instruction: str="", 
        **kwargs
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.instruction= instruction
        if self.model.startswith("Spark"):
            self.spark_configs = {
                "spark_app_id": None,
                "spark_api_key": None,
                "spark_api_secret": None,
                "spark_api_url": SPARK_CONFIG.get(model).get("SPARKAI_URL"),
                "spark_llm_domain": SPARK_CONFIG.get(model).get("SPARKAI_DOMAIN"),
                "streaming": kwargs.get("streaming") if kwargs.get("streaming") else False,
                "temperature": kwargs.get("temperature") if kwargs.get("temperature") else 0.2
            }
            for key, attr in self.spark_configs.items():
                if attr != None:
                    continue
                value = kwargs.get(key)
                if value:
                    self.spark_configs[key] = value
                else:
                    raise ValueError(f"[Error]❌ Please Input the [{key}]")
        else:
            # 添加你自己的模型
            pass
    def extract(self, url: str, html: str, **kwargs):
        soup = html_filter(html=html)
        raw_contents = ''.join(extract_main_content(soup=soup))
        return self.next_run(url=url, res=raw_contents)
    def next_run(self, url: str, res):
        if self.model.startswith("Spark"):
            return self.SparkLLM(contents=res)
        elif self.model == "your_LLM":
            pass
        return super().next_run(url, res)
    def SparkLLM(self, contents: str):
        self.spark_configs["max_tokens"] = self.max_tokens
        spark = ChatSparkLLM(**self.spark_configs)
        messages = [ChatMessage(role="user", content="根据以下内容, 回答问题" 
                                + self.instruction + "简明回答\n" + contents)]
        handler = ChunkPrintHandler()
        res = spark.generate([messages], callbacks=[handler])
        return {"question": self.instruction, "answer": res.generations[0][0].text}
    def to_string(self) -> str:
        return "LLM"
    def params_to_str(self) -> str:
        return super().params_to_str()

class MediaExtractionStrategy(ExtractionStractegy):
    def __init__(
        self, 
        save_path: Union[str, list]=None, 
        save_name: Union[str, list]=None, 
        file_type: Union[str, list]=None
    ):
        if not file_type:
            raise ValueError("file_type shouldn't be None!")
        if isinstance(file_type, list):
            self.file_type = [f.lower() for f in file_type]
            if isinstance(save_path, list) and len(save_path) != len(file_type):
                raise ValueError("Size of file_type and save_path should be the same!")
            if isinstance(save_name, list) and len(save_name) != len(file_type):
                raise ValueError("Size of file_type and save_name should be the same!")
        elif isinstance(file_type, str):
            self.file_type = [file_type.lower()]
        if isinstance(save_path, str):
            os.makedirs(name=save_path, exist_ok=True)
        elif isinstance(save_path, list):
            for dir in save_path:
                os.makedirs(name=dir, exist_ok=True)
        self.save_path = save_path or os.getcwd()
        self.save_name = save_name

    def extract(self, url: str, html: str, **kwargs):
        soup = get_pretty_soup(html)
        crawled_sets = set()
        a_tags = soup.find_all(
            'a', href=lambda href: href and is_media_type(href, self.file_type)
        )
        img_tags = soup.find_all(
            'img', src=lambda src: src and is_media_type(src, self.file_type)
        )
        media_urls = [ urljoin(url, tag['href']) for tag in a_tags] + \
                     [ urljoin(url, tag['src']) for tag in img_tags]
        crawler = kwargs.get("crawler")
        proxy = kwargs.get("proxy")
        for media_url in media_urls:
            if media_url in crawled_sets:
                continue
            content = crawler.crawl(
                url=media_url,
                proxy=proxy,
                content_type="media"
            )
            self.next_run(media_url, content)
            crawled_sets.add(media_url)
        return {}
    def next_run(self, url: str, res):
        auto_name = self.save_name is None
        # 获取文件名和路径
        name = self.save_name or os.path.basename(urlparse(url).path)
        idx = self.file_type.index(get_media_type(url))
        path = self.save_path if isinstance(self.save_path, str) else self.save_path[idx]
        # 如果是自动生成的文件名，则保持原样，否则加上扩展名
        save_name = name if auto_name else f"{name}.{self.file_type[idx]}"
        # 保存文件
        with open(os.path.join(path, save_name), 'wb') as f:
            f.write(res)
        return
    def to_string(self) -> str:
        return super().to_string()
    def params_to_str(self) -> str:
        return super().params_to_str()
