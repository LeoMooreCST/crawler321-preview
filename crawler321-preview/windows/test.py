# test01
from crawler321.run_crawler import RunCrawler
from crawler321.extraction_strategy import *

crawler = RunCrawler()
res = crawler.run(url="http://society.people.com.cn/GB/86800/index.html", encoding="GB2312")
print(res)

# test02
res = crawler.run(url="http://society.people.com.cn/n1/2024/0802/c1008-40291310.html", encoding="GB2312")
print(res)

# test03
'''
    注: 首次启动该用例等待时间比较长, 若出现以下日志, 请耐心等待。过后启动则不需要加载那么长时间
	print("[Logger]🍎 Lauching LocalSeleniumCrawlerStrategy....")
'''
extraction_strategy=XPathExtractionStrategy(
        keys=["书名", "出版社"],
        words=["食南之徒", "湖南文艺出版社"]
    )
res = crawler.run(
    url="https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4",
    extraction_strategy=extraction_strategy
)
print(res)
