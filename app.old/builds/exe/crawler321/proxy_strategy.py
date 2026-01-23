from constant import *

import time
import json
import requests
from abc import ABC, abstractmethod


class ProxyStrategy(ABC):
    '''
        Base models for strategies
        get_proxies: 均采用账号密码验证, 可以根据实际需求替换成自己的
        get_ips:     返回ip池, 示例中均采用json格式
    '''
    def __init__(
        self, 
        ip_api: str="", 
        username: str="", 
        password: str=""
    ):
        self.ip_count = 0      # 当前计数
        self.proxy_lists = []  # 当前可用代理列表
        self.ip_api = ip_api   # 当前代理的api入口
        self.username = username
        self.password = password
    @abstractmethod
    def get_ips(self) -> list:
        pass
    @abstractmethod
    def get_proxies(self) -> dict:
        if self.proxy_lists == [] or self.ip_count > len(self.proxy_lists):
            current_ips = self.get_ips()
            self.proxy_lists = [
                {
                    "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % \
                            {"user": self.username, "pwd": self.password, "proxy": ip},
                    "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % \
                            {"user": self.username, "pwd": self.password, "proxy": ip},
                }
                for ip in current_ips
            ]
            self.ip_count = 0
        self.ip_count += 1
        return self.proxy_lists[self.ip_count - 1]

class NoProxyStrategy(ProxyStrategy):
    def get_ips(self) -> list:
        return []
    def get_proxies(self) -> dict:
        return {}
'''
    如果你有专属ip池, 请使用这种方式进行代理, 为了安全, 建议使用账号密码进行验证
    ip_lists中的ip请以ip: port的格式存放
'''
class SingleProxyStrategy(ProxyStrategy):
    def __init__(
        self, 
        ip_lists: list=[], 
        username="", 
        password=""
    ):
        self.username = username
        self.password = password
        self.ip_lists = ip_lists
    def get_ips(self) -> list:
        return self.ip_lists
    def get_proxies(self) -> dict:
        return super().get_proxies()

'''
    示例: 请根据实际需求修改
    Support By https://www.juliangip.com/, 侵删
    请求返回方式请选择json
'''
class JuLiangProxyStrategy(ProxyStrategy):
    def __init__(
        self, 
        ip_api: str, 
        username: str, 
        password: str
    ):
        super().__init__(ip_api, username, password)
    def get_ips(self) -> list:
        try:
            response = requests.get(
                url=self.ip_api, headers=REQUEST_HEADERS
            )
            return json.loads(response.text).get("data").get("proxy_list")
        except Exception as e:
            print("[Error]❌ Cannot fetch proxies, waiting to retry: ", e)
            time.sleep(5)
            return self.get_ips()
            
    def get_proxies(self) -> dict:
        return super().get_proxies()

'''
    示例: 请根据实际需求修改
    Supported by https://www.jghttp.com/api/duration_api/, 侵删
    请求返回方式请选择json
'''
class JiGuangProxyStrategy(ProxyStrategy):
    def __init__(
        self, 
        ip_api: str, 
        username: str="", 
        password: str=""
    ):
        super().__init__(ip_api, username, password)        
    def get_ips(self) -> list:
        try:
            response = requests.get(
                url=self.ip_api, headers=REQUEST_HEADERS
            )
            return [item["ip"] + ":" + item["port"] for item in
                    json.loads(response.text).get("data")]
        except Exception as e:
            print("[Error]❌ Cannot fetch proxies, waiting to retry: ", e)
            time.sleep(5)
            return self.get_ips()
    def get_proxies(self) -> dict:
        return super().get_proxies()

'''
    示例: 请根据实际需求修改
    Supported by https://http.py.cn/api/api_unlimited/, 侵删
    请求返回方式请选择json
'''
class PinYiProxyStrategy(ProxyStrategy):
    def __init__(self, ip_api: str, username: str="", password: str=""):
        super().__init__(ip_api, username, password)        
    def get_ips(self) -> list:
        try:
            response = requests.get(
                url=self.ip_api, headers=REQUEST_HEADERS
            )
            return [item["ip"] + ":" + item["port"] for item in
                    json.loads(response.text).get("data")]
        except Exception as e:
            print("[Error]❌ Cannot fetch proxies, waiting to retry: ", e)
            time.sleep(5)
            return self.get_ips()
    def get_proxies(self) -> dict:
        return super().get_proxies()

'''
    你可以在此定义你自己的方式, 注意, 无论使用那种方式均从get_proxies()返回最终格式化后的地址
'''