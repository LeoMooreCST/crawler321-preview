from pydantic import BaseModel
from typing import Optional, Union

class TextResult(BaseModel):
    length: int
    content: Union[list, str]

class UrlResults(BaseModel):
    page_num: int
    urls: list

class HTMLResult(BaseModel):
    url: str
    title: Optional[str] = None
    keywords: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    res: Optional[dict] = None

