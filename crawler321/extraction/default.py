from .base import BaseExtraction
from typing import Union
from lxml import etree
from crawler321.utils import extract_raw_html, formalize_result

class DefaultExtraction(BaseExtraction):
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
        return "Default"
    def params_to_str(self) -> str:
        return super().params_to_str()
        