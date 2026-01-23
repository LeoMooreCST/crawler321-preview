from .base import BasePrompt

class SimplePrompt(BasePrompt):
    name = "Simple"

    def __init__(self, question: str):
        self.question = question

    def build(self, content: str) -> str:
        return f"""
            你是信息抽取助手。
            根据以下内容回答问题：
            问题：{self.question}
            内容：
            {content}
            要求：简明、准确
        """
