from utils import *
from constant import *
from data_model import *
import requests
from lxml import etree
from collections import Counter
from abc import ABC, abstractmethod

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
    def __init__(self, xpaths: list=None, content_type: str="text"):
        self.xpaths = xpaths  # 保留了传统xpath的的解析方式 TODO
        self.content_type = content_type
    def extract(self, url: str, html: str):
        content = extract_raw_html(html=html) if self.content_type == "text" else html
        length = len(content)
        return formalize_result(TextResult(length=length,content=content))
    def next_run(self, url: str, res):
        return super().next_run(url, res)
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
        soup = html_filter(html=html)
        alinks = get_a_links(soup=soup, base_url=url)
        # # 进一步优化：
        next_page_url = get_next_pagination(soup=soup, base_url=url)
        if next_page_url:   # 注意需要修正一下
            try:
                resp = requests.get(url=next_page_url, headers=REQUEST_HEADERS)
                resp.encoding = get_charset_of_html(resp.text)
                html_next = resp.text
            except Exception:
                html_next = ""
            soup_next = html_filter(html=html_next)
            alinks_next = get_a_links(soup=soup_next, base_url=next_page_url[0])
            self.common_urls = get_common_urls(alinks, alinks_next)
            alinks = get_diff_urls(origins=alinks, commons=self.common_urls)
        all_urls = formalize_urls(urls=alinks)
        # print("[Logger]🍎 Beginning Excuting clustering_urls()")
        clusters = clustering_urls(urls=all_urls, min_cluster=self.min_len)
        clusters_list = self.handle_clustering(clusters=clusters, urls=all_urls)
        return {i: cluster for i, cluster in enumerate(clusters_list)}
    def next_run(self, url: str, res):
        # TODO: 可以做连爬
        return super().next_run(url, res)
    def handle_clustering(self, clusters, urls) -> list:
        # 获取所有唯一的类标签
        unique_labels = np.unique(clusters)
        clusters_list = []
        if len(unique_labels) == 1:
            cluster_urls = np.array(urls)[clusters == unique_labels[0]]
            urls_list = [url['full_url'] for url in cluster_urls]
            url_contents = [url['content'] for url in cluster_urls]
            clusters_list.append({"urls": urls_list, "titles": url_contents})
        elif self.auto_filter == True:
            # 初始化一个字典来统计每个类的数量
            class_counts = { label: len(np.where(clusters == label)[0]) 
                            for label in unique_labels if label != -1 }
            most_common_class = Counter(class_counts).most_common(1)[0][0]
            # 获取数量最多的类的元素列表
            cluster_urls = np.array(urls)[clusters == most_common_class]
            urls_list = [url['full_url'] for url in cluster_urls]
            url_contents = [url['content'] for url in cluster_urls]
            clusters_list.append({"urls": urls_list, "titles": url_contents})
        else:
            # # 将各个元素放入对应类的列表中
            for label in unique_labels:
                if label != -1:
                    cluster_urls = np.array(urls)[clusters == label]
                    urls_list = [url['full_url'] for url in cluster_urls]
                    url_contents = [url['content'] for url in cluster_urls]
                    clusters_list.append({"urls": urls_list, "titles": url_contents})
        return clusters_list
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
    def __init__(self, model: str=None, objects: list=None):
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
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
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