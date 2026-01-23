from abc import ABC, abstractmethod
from .constant import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from typing import Optional
import time
class SeleniumCommand(ABC):
    def __init__(self, wait=None, until: tuple=None):
        self.wait = wait
        self.until = until if until is not None else (By.TAG_NAME, "body")
    @abstractmethod
    def execute(self, driver):
        pass
    def wait_time(self, driver):
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        if self.wait:
            time.sleep(self.wait)
            return
        if self.until[0] == "keyword":
            key = By.XPATH
            val = f"//*[contains(text(), '{self.until[1]}')]"
        else:
            key = self.until[0]
            val = self.until[1]
        self.web_driver_wait(driver, key, val)
    def web_driver_wait(self, driver, key, value):
        return WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((key, value))
        )
class DefaultCMD(SeleniumCommand):
    def __init__(self, wait=None, until = None):
        super().__init__(wait, until)
    def execute(self, driver):
        return self.wait_time(driver)

# 刷新命令
class RefreshCMD(SeleniumCommand):
    def __init__(self, wait=None, until: tuple=(By.TAG_NAME, "body")):
        super().__init__(wait, until)
    def execute(self, driver):
        driver.refresh()
        self.wait_time(driver)
# 后退命令
class BackCMD(SeleniumCommand):
    def __init__(self, wait=None, until: tuple=(By.TAG_NAME, "body")):
        super().__init__(wait, until)
    def execute(self, driver):
        driver.back()
        self.wait_time(driver)
# 前进命令
class ForwardCMD(SeleniumCommand):
    def __init__(self, wait=None, until: tuple=(By.TAG_NAME, "body")):
        super().__init__(wait, until)
    def execute(self, driver):
        driver.forward()
        self.wait_time(driver)
# 点击命令
class ClickCMD(SeleniumCommand):
    def __init__(self, by, value, wait=None, until: tuple=(By.TAG_NAME, "body")):
        super().__init__(wait, until)
        self.by = by
        self.value = value
    def execute(self, driver):
        elements = []
        if self.by == "keyword":
            try:
                elements = self.web_driver_wait(
                    By.XPATH, f"//*[contains(text(), '{self.value}')]"
                )
            except Exception:
                elements = driver.execute_script(
                    KEYWORDELEMENTSCRIPT, self.value
                )
        else:
            elements = super().web_driver_wait(driver, self.by, self.value)
        # 这里假设所有元素全点:
        for ele in elements:
            ele.click()
        self.wait_time(driver)

# 输入命令
class InputCMD(SeleniumCommand):
    def __init__(self, text, by="keyword", value="input", wait=None, until: tuple=(By.TAG_NAME, "body")):
        super().__init__(wait, until)
        self.text = text
        self.by = by
        self.value = value
    def execute(self, driver):
        elements = super().web_driver_wait(
            driver,
            By.TAG_NAME if self.by == "keyword" else self.by, 
            self.value
        )
        target = None
        if self.by == "keyword":
            import re
            for ele in elements:
                placeholder = ele.get_attribute('placeholder')
                if placeholder and re.search(
                    rf'\b{re.escape(self.value)}\b', re.sub(r'\s+', '', placeholder)
                ):
                    target = ele
        else:
            target = elements[0]
        target.send_keys(self.text)
        self.wait_time(driver)

class UploadCMD(SeleniumCommand):
    def __init__(self,
                 content,
                 by=By.XPATH,
                 value="//input[@type='file']",
                 wait=None, 
                 until = (By.TAG_NAME, "body")):
        super().__init__(wait, until)
        self.content = content
        self.by = by
        self.value = value
    def execute(self, driver):
        element = super().web_driver_wait(driver, self.by, self.value)
        element.send_keys(self.content)
        self.wait_time(driver)
# 滚动命令
class ScrollCMD(SeleniumCommand):
    def __init__(self, duration, wait=None, until = (By.TAG_NAME, "body")):
        super().__init__(wait, until)
        self.JSobj = JsCMD(js="window.scrollTo(0, document.body.scrollHeight);", wait=0.5)
        self.duration = duration
    def execute(self, driver):
        start_time = time.time()
        while time.time() - start_time < self.duration:
            self.JSobj.execute(driver)
        
# js命令
class JsCMD(SeleniumCommand):
    def __init__(self, js, wait=None, until = (By.TAG_NAME, "body")):
        super().__init__(wait, until)
        self.js = js
    def execute(self, driver):
        try:
            driver.execute_script(self.js)
        except Exception as e:
            print(e)
        self.wait_time(driver)
# 停止命令
class QuitCMD(SeleniumCommand):
    def __init__(self, wait=None, until = (By.TAG_NAME, "body")):
        super().__init__(wait, until)
    def execute(self, driver):
        driver.quit()
# 下载命令
class DownloadCMD(SeleniumCommand):
    def __init__(self, wait=None, until = (By.TAG_NAME, "body")):
        super().__init__(wait, until)
    def execute(self, driver):
        # TODO
        pass