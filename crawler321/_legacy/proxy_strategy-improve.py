# -------------------------------
# IP轮询器 (IP Rotator)
# -------------------------------
class IPRotator:
    def __init__(self, ips: list, username="", password=""):
        self.username = username
        self.password = password
        self.ip_list = ips
        self.index = 0

    def next_proxy(self) -> dict:
        if not self.ip_list:
            return {}
        ip = self.ip_list[self.index]
        self.index = (self.index + 1) % len(self.ip_list)
        if self.username and self.password:
            return {
                "http": f"http://{self.username}:{self.password}@{ip}/",
                "https": f"http://{self.username}:{self.password}@{ip}/"
            }
        else:
            return {"http": f"http://{ip}/", "https": f"http://{ip}/"}

# -------------------------------
# Adapter 改进
# -------------------------------
class JuLiangAdapter(ProxyAdapter):
    def __init__(self, api: JuLiangAPI):
        self.api = api
        self.rotator = None

    def get_proxies(self) -> dict:
        if self.rotator is None:
            ips = self.api.fetch()
            self.rotator = IPRotator(ips, username=self.api.username, password=self.api.password)
        return self.rotator.next_proxy()


class JiGuangAdapter(ProxyAdapter):
    def __init__(self, api: JiGuangAPI):
        self.api = api
        self.rotator = None

    def get_proxies(self) -> dict:
        if self.rotator is None:
            ips = self.api.fetch()
            self.rotator = IPRotator(ips)
        return self.rotator.next_proxy()


class PinYiAdapter(ProxyAdapter):
    def __init__(self, api: PinYiAPI):
        self.api = api
        self.rotator = None

    def get_proxies(self) -> dict:
        if self.rotator is None:
            ips = self.api.fetch()
            self.rotator = IPRotator(ips)
        return self.rotator.next_proxy()
