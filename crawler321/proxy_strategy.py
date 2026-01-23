import time
import json
import requests
from abc import ABC, abstractmethod
from .constant import *

# -------------------------------
# Adaptee（原生代理API）
# -------------------------------
class JuLiangAPI:
    def __init__(self, ip_api, username, password):
        self.ip_api = ip_api
        self.username = username
        self.password = password

    def fetch(self):
        try:
            response = requests.get(url=self.ip_api, headers=REQUEST_HEADERS)
            return json.loads(response.text).get("data").get("proxy_list")
        except Exception as e:
            print("[Error]❌ JuLiangAPI fetch failed:", e)
            time.sleep(5)
            return self.fetch()

class JiGuangAPI:
    def __init__(self, ip_api, username="", password=""):
        self.ip_api = ip_api

    def fetch(self):
        try:
            response = requests.get(url=self.ip_api, headers=REQUEST_HEADERS)
            return [f"{item['ip']}:{item['port']}" for item in json.loads(response.text).get("data")]
        except Exception as e:
            print("[Error]❌ JiGuangAPI fetch failed:", e)
            time.sleep(5)
            return self.fetch()

class PinYiAPI:
    def __init__(self, ip_api, username="", password=""):
        self.ip_api = ip_api

    def fetch(self):
        try:
            response = requests.get(url=self.ip_api, headers=REQUEST_HEADERS)
            return [f"{item['ip']}:{item['port']}" for item in json.loads(response.text).get("data")]
        except Exception as e:
            print("[Error]❌ PinYiAPI fetch failed:", e)
            time.sleep(5)
            return self.fetch()

# -------------------------------
# Adapter 抽象类
# -------------------------------
class ProxyAdapter(ABC):
    @abstractmethod
    def get_proxies(self) -> dict:
        pass

# -------------------------------
# 具体Adapter
# -------------------------------
class JuLiangAdapter(ProxyAdapter):
    def __init__(self, api: JuLiangAPI):
        self.api = api
        self.ip_count = 0
        self.proxy_lists = []

    def get_proxies(self) -> dict:
        if not self.proxy_lists or self.ip_count >= len(self.proxy_lists):
            ips = self.api.fetch()
            self.proxy_lists = [
                {
                    "http": f"http://{self.api.username}:{self.api.password}@{ip}/",
                    "https": f"http://{self.api.username}:{self.api.password}@{ip}/",
                }
                for ip in ips
            ]
            self.ip_count = 0
        proxy = self.proxy_lists[self.ip_count]
        self.ip_count += 1
        return proxy

class JiGuangAdapter(ProxyAdapter):
    def __init__(self, api: JiGuangAPI, username="", password=""):
        self.api = api
        self.username = username
        self.password = password
        self.ip_count = 0
        self.proxy_lists = []

    def get_proxies(self) -> dict:
        if not self.proxy_lists or self.ip_count >= len(self.proxy_lists):
            ips = self.api.fetch()
            self.proxy_lists = [
                {"http": f"http://{ip}/", "https": f"http://{ip}/"} for ip in ips
            ]
            self.ip_count = 0
        proxy = self.proxy_lists[self.ip_count]
        self.ip_count += 1
        return proxy

class PinYiAdapter(ProxyAdapter):
    def __init__(self, api: PinYiAPI, username="", password=""):
        self.api = api
        self.username = username
        self.password = password
        self.ip_count = 0
        self.proxy_lists = []

    def get_proxies(self) -> dict:
        if not self.proxy_lists or self.ip_count >= len(self.proxy_lists):
            ips = self.api.fetch()
            self.proxy_lists = [
                {"http": f"http://{ip}/", "https": f"http://{ip}/"} for ip in ips
            ]
            self.ip_count = 0
        proxy = self.proxy_lists[self.ip_count]
        self.ip_count += 1
        return proxy

# -------------------------------
# 无代理适配器
# -------------------------------
class NoProxyAdapter(ProxyAdapter):
    def get_proxies(self) -> dict:
        return {}
