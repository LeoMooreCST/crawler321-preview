# crawler321-preview v0.1.0

**crawler321 预览版 一定程度上简化了爬虫过程，引入精细化的页面内容提取策略和个性化自定义提取策略，同时引入大语言模型，让网页信息获取更加方便便捷，希望通过像数数"1,2,3"一样即可获取你想要的信息**

> **提示**：该项目目前处于建设测试阶段，因某些原因暂不能公开完整源码，还望见谅！但提供windows和linux环境下的使用，目前公开的项目完全免费自由使用，详见"安装使用"部分。

## 💎 功能和特性

* **✏️支持精细化和个性化的提取策略，满足丰富多样的场景需求：如结构化数据、目录型、内容型等**
* **🎯简单而高效的操作，能够自动识别各种各样的网页类型，甚至不用自己指定策略！**
* **🗒️灵活稳定的结果输出：自动提取网页元数据，以json缩进形式输出**
* **⚒️友好的用户交互方式：简单的命令让机器像人一般操控网页，如点击、输入、刷新等操作**
* **👼触手可及的人工智能：引入大语言模型，一句话就轻松获取自己最想要的内容**
* **🪄强大的数据备份机制：可提供数据本地存储机制，即使发生中断也能快速获取历史数据**
* **📊丰富充实的数据报告：让你快速定位未成功的请求，多样化的统计数据分析整个crawl过程**
* **📌一键使用的代理策略：能让你迅速摆脱同一机器请求次数过多的问题**

## 🔧 安装使用

基本要求：python >= 3.8，参考安装教程中使用venv创建虚拟教程，也建议使用此方式。

```powershell
# 克隆项目
git clone https://github.com/LeoMooreCST/crawler321-preview.git
```

gitee请查看：[LeoMooreCST/crawler321-preview ](https://gitee.com/LeoMooreCST/crawler321-preview.git)

### 1. Windows环境

我们简化了安装过程

- **第一步**：进入crawler321-preview/windows文件夹。在powershell终端中(不是cmd)，执行：

```powershell
.\install.ps1
```

    **或者**在cmd中**依次执行**以下命令：

```powershell
python -m venv ./
.\Scripts\activate
mv .\crawler321\ .\Lib\site-packages\
mv .\crawler321-0.1.0.dist-info\ .\Lib\site-packages\
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/  
pip install --upgrade spark_ai_python -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

> 该过程大约7-15分钟左右，请耐心等待。
>
> 此过程若出现以下错误，可忽略。

```powershell
ERROR: opentelemetry-proto 1.26.0 has requirement protobuf<5.0,>=3.19, but you'll have protobuf 5.27.3 which is incompatible.
ERROR: opentelemetry-api 1.26.0 has requirement importlib-metadata<=8.0.0,>=6.0, but you'll have importlib-metadata 8.2.0 which is incompatible.
ERROR: llama-index-core 0.10.59 has requirement tenacity!=8.4.0,<9.0.0,>=8.2.0, but you'll have tenacity 9.0.0 which is incompatible.  
ERROR: llama-index-legacy 0.9.48 has requirement tenacity<9.0.0,>=8.2.0, but you'll have tenacity 9.0.0 which is incompatible.
```

- **第二步**：
  - 如果主机上已经有了chrome浏览器, 但未chromedriver，在[Chrome for Testing availability (googlechromelabs.github.io)](https://googlechromelabs.github.io/chrome-for-testing/)下载对应版本(在chrome浏览器查看版本，若不是最新的更新即可)的chromedriver，将chromedriver添加到环境变量即可
    **注**：本地的chrome可能会自动更新，导致chromedriver需要频繁更新，一种解决方法就是关闭chrome的自动更新
  - 如果主机没有chrome浏览器，在[Chrome for Testing availability (googlechromelabs.github.io)](https://googlechromelabs.github.io/chrome-for-testing/)下载chrome和chromdriver解压后文件夹为:  E:\chrome-win64 (直接包含chrome.exe), E:\chromedriver-win64(直接包含chromedriver.exe), win11中：设置 -> 系统 -> 高级系统设置 -> 环境变量 -> 系统变量(S) -> Path 添加即可
  - 如果你不知道如何添加环境变量，将下载的zip放在此文件夹，在powershell中执行如下（过程需要管理员权限，多次点击确认即可）即可：
    ```powershell
    .\chrome.ps1
    ```

> 如果上述过程未报错，即环境安装成功，可对环境进行测试

### 2. linux(推荐WSL)

进入crawler321-preview/linux文件夹，执行如下命令即可：

```bash
source install.bash
```

> 该过程大约7-15分钟左右，请耐心等待
>
> 如果上述过程未报错，即环境安装成功

**注：以上均在python虚拟环境下进行，会自动创建虚拟环境，无需手动创建。编译器对该项目包中导入库的使用出现的报错现象均为正常，可忽略掉**。

### 3. 环境测试

依次执行以下python测试用例：

```python
# test01
from crawler321.run_crawler import RunCrawler
crawler = RunCrawler()
res = crawler.run(url="http://society.people.com.cn/GB/86800/index.html", encoding="GB2312")
print(res)
```

```python
# test02
from crawler321.run_crawler import RunCrawler
crawler = RunCrawler()
res = crawler.run(url="http://society.people.com.cn/n1/2024/0802/c1008-40291310.html", encoding="GB2312")
print(res)
```

```python
# test03
'''
    注: 首次启动该用例等待时间比较长, 若出现以下日志, 请耐心等待。过后启动则不需要加载那么长时间
	print("[Logger]🍎 Lauching LocalSeleniumCrawlerStrategy....")
'''
from crawler321.run_crawler import RunCrawler
from crawler321.extraction_strategy import *
crawler = RunCrawler()
extraction_strategy=XPathExtractionStrategy(
        keys=["书名", "出版社"],
        words=["食南之徒", "湖南文艺出版社"]
    )
res = crawler.run(
    url="https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4",
    extraction_strategy=extraction_strategy
)
print(res)
```

> 注：以上测试用例所涉及网址均为学习使用，无任何其他用途，侵删。

若以上用例均能有正常内容输出，则恭喜你基本环境安装成功，解析来开启你的探索之旅吧！

## ✨ 快速入手

### 示例1：什么也不用做

```
import json
from crawler321.run_crawler import RunCrawler
crawler = RunCrawler()
result = crawler.run(url="https://www.demo.com")
result = json.loads(result)
print(result["res"])
```

### 示例2：只想提取结构化数据

```
import json
from crawler321.extraction_strategy import ObjectExtractionStrategy
from crawler321.run_crawler import RunCrawler
crawler = RunCrawler()
extraction_strategy = ObjectExtractionStrategy(objects=["姓名","邮箱"]) # 只返回"姓名"和"邮箱"
result = crawler.run(
    url="https://www.demo.com",
    extraction_strategy=extraction_strategy
)
result = json.loads(result)
print(result["res"])
```

### 示例3：让机器像人一样操作

```
from crawler321.crawler_strategy import SeleniumCrawlerStrategy
from crawler321.run_crawler import RunCrawler
from crawler321.action import By, Do, SeleniumAction
crawler = RunCrawler(
    crawler_strategy=SeleniumCrawlerStrategy()
)
actions = [
    SeleniumAction(action=Do.INPUT, target={By.KEY_WORD: "请输入账号"}, content="123456", wait=2)
    SeleniumAction(action=Do.REFRESH)
]
crawler.run(
    url="https://www.page1.com",
    actions=actions
)

```

## 📖 使用手册

更多功能和特性请关注使用手册：[crawler321使用手册](https://kdocs.cn/l/cdvZUdxSmJwe "正在健全和完善中")

## 📧 联系方式

- ❔ 奈何一人能力水平有限，若在安装和使用过程遇到任何问题，可在仓库评论区留言，作者将尽力解答。
- ✏️ 因处于预览版，很多功能和文档可能还不够完善和成熟，若有更好的建议或者意见，可联系作者邮箱：princekinqiang@163.com，亮点部分被采纳的话作者有小奖励哦！
- 🐧 由于该工具处于起步阶段，一个人的智慧是有限的，一群人的力量才是强大的。作者z真诚希望能遇到更多优秀的爱好者们加入到此工具的开发和完善之中，有意者可联系邮箱：princekinqiang@163.com (备注来意)

## Acknowledgements 致谢

- This project incorporates design elements and concepts from [crawl4ai](https://github.com/unclecode/crawl4ai?tab=readme-ov-file) by unclecode, which is licensed under the Apache License 2.0. We thank the original authors for their contribution to the open-source community. The design and structure provided valuable guidance for this project. We declare that the implements and contents were done on our own. Note that this project is licensed under AGPLv3.
- 我们非常感谢[星火Spark大模型](https://xinghuo.xfyun.cn/sparkapi)提供的API，在我们的项目中有所引用，详见使用手册，若有侵权，联系即删【仅作学习使用，无任何其他用途】
- 我们非常感谢[巨量](https://www.juliangip.com/)、[极光](https://www.jghttp.com/)和[品易](https://http.py.cn/)(排名不分先后)提供的接口服务，在我们的项目中有所引用，详见使用手册，若有侵权，联系即删【仅作学习使用，无任何其他用途】

> 注：该工具不提供任何不合法功能，仅用作学习使用，请大家自觉合理合法使用！
>
> 喜欢的可以给作者点个小⭐⭐！
