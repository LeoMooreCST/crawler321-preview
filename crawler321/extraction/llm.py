from .base import BaseExtraction
from crawler321.llm.registry import adapter_registry
from crawler321.llm.prompt import BasePrompt
from crawler321.utils import html_filter, extract_main_content

class LLMExtraction(BaseExtraction):
    def __init__(self, config, prompt: BasePrompt, max_tokens=128):
        self.prompt = prompt
        self.max_tokens = max_tokens
        self._adapter = adapter_registry.create_adapter(config=config)

    def extract(self, url, html, **kwargs):
        soup = html_filter(html=html)
        raw_contents = ''.join(extract_main_content(soup=soup))
        question = self.prompt.build(raw_contents)
        return {"answer": self._adapter.generate(question, self.max_tokens)}

    def next_run(self, url, res):
        return super().next_run(url, res)
    def to_string(self):
        return "llm-Extraction"