import sys, time, requests
from utils import *
from proxy_strategy import *
from constant import *
from crawler321._legacy.action import SeleniumAction
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
        print("[Logger]🍎 Lauched webdriver-chrome")
        if headers.get("Cookies"):
            for cookie in headers.get("Cookies"):
                self.driver.add_cookie(cookie)
        self.action_map = {
            "scroll": self.scroll,
            "js": self.js,
            "refresh": self.refresh,
            "back": self.back,
            "forward": self.forword,
            "click": self.click,
            "input": self.input,
            "upload": self.upload,
            "download": self.download
        }
        self.by_map = {
            "id": By.ID,
            "xpath": By.XPATH,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR
        }
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
            self.actions = kwargs.get("actions") or [SeleniumAction(action="scroll", duration=5)]
            start_time = time.time()
            # 等待加载
            print("waiting")
            self.driver.get(url=url)
            self.wait_time(action=SeleniumAction(action="None"))
            for action in self.actions:
                action_method = self.action_map.get(action.action)
                if not action_method:
                   raise ValueError(f"Invalid action name: {action.action} in LocalSeleniumCrawlerStrategy->crawl()")
                if action.action in ["refresh", "back", "forward"]:
                   action_method()
                else:
                   action_method(action)
                self.wait_time(action=action)

            print(f"[Logger]🍎 LocalSeleniumCrawlerStrategy: Fetched HTML, time:{time.time() - start_time}s")
            return self.driver.page_source 
        except Exception as e:
            print("[Error]❌ Getting crawl wrong -> LocalSeleniumCrawlerStrategy(): ", e)
        return ""
    def get_cookies(self):
        return self.driver.get_cookies()
    def wait_time(self, action: SeleniumAction):
        WebDriverWait(self.driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        if action.wait:
            # print(action.wait)
            time.sleep(action.wait)
            # self.driver.implicitly_wait(action.wait)
        elif action.until:
            if action.until.get("keyword"):
                self.web_driver_wait(
                    By.XPATH, f"//*[contains(text(), '{action.until.get('keyword')}')]"
                )
            else:
                self.web_driver_wait(
                    self.by_map.get(list(action.until.keys()[0])), list(action.until.values()[0])
                )
        else:
            self.web_driver_wait(By.TAG_NAME, "body")
    def web_driver_wait(self, key, value):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((key, value))
        )
    def js(self, js_code: str):
        try:
            self.driver.execute_script(js_code)
        except Exception as e:
            print(e)
    def scroll(self, action: SeleniumAction):
        start_time = time.time()
        while (time.time() - start_time) < action.duration:
            self.js("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
    def refresh(self):
        self.driver.refresh()
    def back(self):
        self.driver.back()
    def forword(self):
        self.driver.back()
    def click(self, action: SeleniumAction):
        if not action.target:
            raise KeyError("Invalid action: Unknown target")
        key = list(action.target.keys())[0]
        value = list(action.target.values())[0]
        if key == "keyword":
            try:
                elements = self.web_driver_wait(
                    By.XPATH, f"//*[contains(text(), '{value}')]"
                )
            except Exception:
                elements = self.driver.execute_script(
                    KEYWORDELEMENTSCRIPT, value
                )
        else:
            elements = self.web_driver_wait(key, value)
        if action.content and action.content == "all":
            for element in elements:
                element.click()
        else:
            elements[0].click()
    def input(self, action: SeleniumAction):
        if not action.target or list(action.target.keys())[0] == "keyword":
            elements = self.web_driver_wait(By.TAG_NAME, "input")
        else:
            elements = self.web_driver_wait(
                self.by_map.get(list(action.target.keys())[0]),
                list(action.target.values())[0]
            )
        if action.target and list(action.target.keys())[0] == "keyword":
            for element in elements:
                placeholder = element.get_attribute('placeholder')
                if placeholder and re.search(
                    rf'\b{re.escape(list(action.target.values())[0])}\b',
                    re.sub(r'\s+', '', placeholder)
                ):
                    element.send_keys(action.content)
                    return
        element = elements[0]
        element.send_keys(action.content)

    def upload(self, action):
        if not action.target or list(action.target.keys())[0] == "keyword":
            elements = self.web_driver_wait(By.XPATH, "//input[@type='file']")
        else:
            elements = self.web_driver_wait(
                self.by_map.get(list(action.target.keys())[0]),
                list(action.target.values())[0]
            )
        element = elements[0]
        element.send_keys(action.content)
    
    def download(self, action):
        # download_files(html=self.driver.page_source, url=self.driver.current_url, type=action.content)
        pass
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
    
    def quit(self):
        self.driver.quit()

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

