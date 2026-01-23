import sys, time, requests
from utils import *
from proxy_strategy import *
from constant import *

from abc import ABC, abstractmethod

from PyQt5.QtCore import QThread

class CrawlerStrategy(ABC):
    @abstractmethod
    def crawl(
        self, 
        url: str, 
        method: str="GET", 
        params=None,
        data=None,
        encoding=None, 
        proxy=False,
        **kwargs
    ) -> str:
        pass

'''
    传统的requests.get(url, )
'''
class RequestsCrawlerStrategy(CrawlerStrategy):
    def __init__(self, proxy_strategy=None, **kwargs):
        print("[Logger]🍎 Launching LocalRequestsCrawlerStrategy.")
        self.proxy_strategy = proxy_strategy or NoProxyStrategy()
        self.session = requests.Session()
        self.session.headers = kwargs.get("headers") or REQUEST_HEADERS
 
    def crawl(
        self, 
        url: str, 
        method: str="GET", 
        params=None,
        data=None,
        encoding=None, 
        proxy=False,
        max_retries=20,
        **kwargs
    ) -> str:
        try:
            response = self.session.request(
                url=url, 
                method=method, 
                params=params, 
                data=data
            )
            code = response.status_code
            if code == StatusCode.OK.value:
                return self.__process_response(response, encoding)
            elif code == StatusCode.NOT_FOUND.value:
                print(f"[404]{StatusCode.NOT_FOUND.name}: {url}")
                return ""
            elif code == StatusCode.TOOMANYREQUESTS.value:
                print(f"[429]{StatusCode.TOOMANYREQUESTS.name}: You are crawling too heavily")
                sys.exit()
            elif code in [StatusCode.BAD_REQUEST.value, StatusCode.FORBIDDEN.value]:
                if proxy:
                    return self.__get_proxy_response(
                        url, method, params, data, max_retries, encoding
                    )
                else:
                    print(f"[{self.status_code}]crawler error: {url}")
        except Exception as e:
            print(f"[{self.status_code}]crawler error: {url}, {e}")
            if proxy:
                return self.__get_proxy_response(
                    url, method, params, data, max_retries, encoding
                )
    def __get_proxy_response(
        self, 
        url: str, 
        method: str, 
        params,
        data,
        max_retries: int, 
        encoding: str
    ):
        attempts = 0
        while attempts < max_retries:
            try:
                response = self.session.request(
                    url=url, 
                    method=method,
                    params=params,
                    data=data,
                    proxies=self.proxy_strategy.get_proxies()
                )
                if response.status_code == StatusCode.OK.value:
                    return self.__process_response(response, encoding)
            except requests.exceptions.RequestException:
                print("[Logger]🍎 Bad response, Needing a new ip......")
            attempts += 1
        print("Max retries reached, unable to get a valid response")
        return ""

    def __process_response(
        self, 
        response: requests.Response, 
        encoding: str
    ) -> str:
        charset = get_charset_of_html(response.text)
        response.encoding = encoding or charset or DEFAULT_CHARSET
        return response.text

