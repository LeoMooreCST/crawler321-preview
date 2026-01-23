import sys, time, requests
from .utils import *
from .proxy_strategy import *
from .constant import *
from .SeleniumCommand import *
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from typing import List, Any
from collections.abc import Iterable
class CrawlerStrategy(ABC):
    @abstractmethod
    def crawl(
        self, 
        url: str, 
        method: str="GET",
        content_type: str="text",
        params=None,
        data=None,
        encoding=None, 
        proxy=False,
        max_retries=20,
        **kwargs
    ):
        pass

class SeleniumCrawlerStrategy(CrawlerStrategy):
    def __init__(self, headless=True, **kwargs):
        print("[Logger]🍎 Lauching LocalSeleniumCrawlerStrategy....")
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        headers = kwargs.get("headers") or REQUEST_HEADERS
        self.options.add_argument(f"user-agent={headers.get('User-Agent')}")
        self.arguments = [
            "--log-level=3",
            "--disable-gpu",
            "--disable-notifications",
            "--window-size=1920,1080",
            # "--disable-cache", 
            "--no-sandbox",
            "--disable-extensions"
        ]
        for argument in self.arguments:
            self.options.add_argument(argument) 
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.back()
        print("[Logger]🍎 Lauched webdriver-chrome")
        if headers.get("Cookies"):
            for cookie in headers.get("Cookies"):
                self.driver.add_cookie(cookie)
        self.commands: List[SeleniumCommand] = []
        # 保留选项
        # self.by_map = {
        #     "id": By.ID,
        #     "xpath": By.XPATH,
        #     "link": By.LINK_TEXT,
        #     "partial_link": By.PARTIAL_LINK_TEXT,
        #     "name": By.NAME,
        #     "tag": By.TAG_NAME,
        #     "class": By.CLASS_NAME,
        #     "css": By.CSS_SELECTOR
        # }
    def addCMD(self, cmd: Any):
        if isinstance(cmd, SeleniumCommand):
            self.commands.append(cmd)
        elif isinstance(cmd, Iterable) and not isinstance(cmd, (str, bytes)):
            for i, item in enumerate(cmd):
                if not isinstance(item, SeleniumCommand):
                    raise TypeError(
                    f"Element at position {i} is not a SeleniumCommand: "
                    f"got {type(item).__name__}"
                    )
            self.commands.extend(cmd)
        else:
            raise TypeError(
                f"Expected SeleniumCommand or iterable of SeleniumCommand, "
                f"got {type(cmd).__name__}"
            )
    def removeCMD(self, idx: List[int] = None):
        if idx is None:
            self.commands.clear()
            return
        for i in sorted(set(idx), reverse=True):
            if 0 <= i < len(self.commands):
                del self.commands[i]
    def crawl(
        self, 
        url: str, 
        method: str="GET",
        content_type: str="text",
        params=None,
        data=None,
        encoding=None, 
        proxy=False,
        max_retries=20,
        **kwargs
    ):
        try:
            start_time = time.time()
            # 等待加载
            print("waiting")
            self.driver.get(url=url)
            DefaultCMD(wait=0.1).execute(self.driver)
            # 执行动作: 命令模式解耦合
            for command in self.commands:
                command.execute(self.driver)
            print(f"[Logger]🍎 LocalSeleniumCrawlerStrategy: Fetched HTML, time:{time.time() - start_time}s")
            return self.driver.page_source 
        except Exception as e:
            print("[Error]❌ Getting crawl wrong -> LocalSeleniumCrawlerStrategy(): ", e)
        return ""
    def get_cookies(self):
        return self.driver.get_cookies()
    def find_element_xpath(self, keyword: str) -> list:
        elements = self.driver.find_elements(
            By.XPATH, f"//*[contains(text(), '{keyword}')]"
        )
        if elements:
            xpaths = [
                self.driver.execute_script(AbsoluteXPATHString, element)
                for element in elements
            ]
            return xpaths
        print(f"[Warnning]⚠ Not Found keyword: {keyword}")
        return []


'''
    传统的requests.get(url, )
'''
class RequestsCrawlerStrategy(CrawlerStrategy):
    def __init__(self, proxy_strategy=None, **kwargs):
        print("[Logger]🍎 Launching LocalRequestsCrawlerStrategy.")
        self.proxy_strategy = proxy_strategy or NoProxyAdapter()
        self.session = requests.Session()
        self.session.headers = kwargs.get("headers") or REQUEST_HEADERS
 
    def crawl(
        self, 
        url: str, 
        method: str="GET",
        content_type: str="text",
        params=None,
        data=None,
        encoding=None, 
        proxy=False,
        max_retries=20,
        **kwargs
    ):
        try:
            response = self.session.request(
                url=url, 
                method=method, 
                params=params, 
                data=data
            )
            code = response.status_code if content_type == "text" else 200
            if code == StatusCode.OK.value:
                if content_type == "text":
                    return self.__process_response(response, encoding), 200
                else:
                    return response.content
            elif code == StatusCode.NOT_FOUND.value:
                print(f"[404]{StatusCode.NOT_FOUND.name}: {url}")
                return "", 404
            elif code == StatusCode.TOOMANYREQUESTS.value:
                print(f"[429]{StatusCode.TOOMANYREQUESTS.name}: You are crawling too heavily")
                sys.exit()
            elif code in [StatusCode.BAD_REQUEST.value, StatusCode.FORBIDDEN.value]:
                if proxy:
                    return self.__get_proxy_response(
                        url, method, content_type, params, data, max_retries, encoding
                    )
                else:
                    print(f"[{code}]crawler error: {url}")
                    return "", code

        except Exception as e:
            print(f"[{code}]crawler error: {url}, {e}")
            if proxy:
                return self.__get_proxy_response(
                    url, method, params, data, max_retries, encoding
                )
            else:
                return "", code
    def __get_proxy_response(
        self, 
        url: str, 
        method: str,
        content_type: str,
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
                    if content_type == "text":
                        return self.__process_response(response, encoding), 200
                    else:
                        return response.content
            except requests.exceptions.RequestException:
                print("[Logger]🍎 Bad response, Needing a new ip......")
            attempts += 1
        print("Max retries reached, unable to get a valid response")
        return "", response.status_code

    def __process_response(
        self, 
        response: requests.Response, 
        encoding: str
    ) -> str:
        charset = get_charset_of_html(response.text)
        response.encoding = encoding or charset or DEFAULT_CHARSET
        return response.text

