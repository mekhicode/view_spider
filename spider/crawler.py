from spider import TofoSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spider import ShopbopTempSpider


def start_other(url):
    settings = get_project_settings()
    crawler = CrawlerProcess(settings)
    crawler.crawl(ShopbopTempSpider, url)
    crawler.start()

def start():
    # settings = get_project_settings()
    # crawler = CrawlerProcess(settings)
    # for spider in crawler.spiders.list():
    #     crawler.crawl(spider)
    #     crawler.start()

    settings = get_project_settings()
    crawler = CrawlerProcess(settings)
    crawler.crawl(TofoSpider)
    crawler.start()