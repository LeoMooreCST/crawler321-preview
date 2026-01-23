from pydantic import BaseModel
from typing import Optional
class By:
    KEY_WORD = "keyword"
    ID = "id"
    XPATH = "xpath"
    PARTIAL_LINK = "partial_link"
    NAME = "name"
    TAG = "tag"
    CLASS = "class"
    CSS = "css"

class Do:
    SCROLL = "scroll"
    JS = "js"
    REFRESH = "refresh"
    BACK = "back"
    FORWARD = "forward"
    CLICK = "click"
    INPUT = "input"
    UPLOAD = "upload"
    DOWNLOAD = "download"

class SeleniumAction(BaseModel):
    action: str
    duration: Optional[int] = None
    wait: Optional[int] = None
    target: Optional[dict] = None
    until: Optional[dict] = None
    content: Optional[str] = None