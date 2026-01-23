from pydantic import BaseModel
from typing import Union
class TextResult(BaseModel):
    length: int
    content: Union[list, str]