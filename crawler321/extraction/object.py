from .base import BaseExtraction
from crawler321.utils import html_filter, html_object_encoding, extract_object_pairs
'''
    键值-实体提取模型: 适用于网页中存在"key: value"且为核心内容

    :param model: 提取模型, 默认为local      opt
    :param objects: 需要保留的对象 -> list[] opt
    :return ...
'''
class ObjectExtraction(BaseExtraction):
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