# -*- coding: utf-8 -*-

# Scrapy settings for tofo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

SPIDER_MODULES = ['spider']
NEWSPIDER_MODULE = 'spider'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# 重试次数
RETRY_TIMES = 5

# redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# 禁用cookies
COOKIES_ENABLED = False

CONCURRENT_REQUESTS = 32
DEPTH_PRIORITY = 0
DNSCACHE_ENABLED = True
DNS_TIMEOUT = 10
DOWNLOAD_TIMEOUT = 600

# 下载延迟
DOWNLOAD_DELAY = 0

# mq 地址
RABBIT_HOST = 'localhost'

# pipline settings
ITEM_PIPELINES = {
    'spider.pipelines.ItemFilterPipeline': 275,
    'spider.pipelines.ItemCleanerPipeline': 300,
    'spider.pipelines.ItemRabbitmqPipeline': 325,
}

# 下载器中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
    'spider.download_middlewares.RotateUserAgentMiddleware': 400,
    'spider.download_middlewares.InfiniteRetryMiddleware': 500,
}

# 将链接缓存到redis中，实现分布式队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 永久保存（首次）
SCHEDULER_PERSIST = False
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
# 在分布式爬虫系统下，设置最大空闲时间阻止爬虫关闭
# SCHEDULER_IDLE_BEFORE_CLOSE = 10

# Sentry setting
# SENTRY_DSN = 'http://1d937bbdcbab450490acf73358504b24:ffe71d5b1e3145bab63d657cc25bdf03@123.57.42.1:9000/2'
# EXTENSIONS = {
#     "scrapy_sentry.extensions.Errors": 50,
# }
