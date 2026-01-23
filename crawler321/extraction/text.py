from .base import BaseExtraction
from .data_model import TextResult
from crawler321.utils import *

'''
    提取一个页面的核心内容, 比如新闻网站, 可以使用自定义模型进行提取

    :param model: 提取模型
 
    :return ...
'''
class TextExtraction(BaseExtraction):
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
