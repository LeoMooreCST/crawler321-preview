from .base import BaseExtraction
from typing import Union
from crawler321.utils import *
import os
from urllib.parse import urlparse

class MediaExtraction(BaseExtraction):
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