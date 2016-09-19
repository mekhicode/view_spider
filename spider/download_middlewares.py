# encoding: utf-8

import random
import base64
import logging
import redis

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
# from fake_useragent import UserAgent

# logging init
from spider_logging import main_logging
log = main_logging.Logging()

try:
    import local_settings as settings
except Exception, e:
    import settings

logger = logging.getLogger(__name__)

class RotateUserAgentMiddleware(UserAgentMiddleware):
    """ 随机UserAgent """
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        user_agent_list = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/42.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/50.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/49.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/49.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/49.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/49.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/49.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/49.0.1055.1 Safari/535.24"
        ]

        ua = random.choice(user_agent_list)
        if ua:
            request.headers.setdefault('User-Agent', ua)


class ProxyMiddleware(object):
    """ ip代理 """
    def process_request(self, request, spider):
        proxy = random.choice(spider.settings.getlist('PROXIES'))
        if proxy['user_pass'] is not None:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        else:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']

class InfiniteRetryMiddleware(RetryMiddleware):
    """ 网络错误或者被ban导致链接502或504，将链接重新publish到kafka，实现无限递归爬取 """

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        retryreq = request.copy()
        if retries <= self.max_retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            log.log("0", "spider_retry_log", {'request': request.url, 'retries': retries, 'reason': str(reason), 'spider': spider.name})
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            if retryreq.meta.get('sku'):
                # sku存在，详细信息，放弃循环爬取
                # TODO：无限加入爬虫优先队列
                logger.error("Gave up detail retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
                log.log("3", "spider_retry_log", {'request': request.url, 'retries': retries, 'reason': str(reason), 'spider': spider.name})
                return

            source = spider.name
            url = request.url
            type = 'retry'
            try:
                log.log("1", "spider_retry_log", {'url': url, 'type': type, 'reason': str(reason), 'source': source})
            except:
                logger.error("Gave up detail retrying %(request)s (failed %(retries)d times): %(reason)s , url: %(url)s",
                         {'request': request, 'retries': retries, 'reason': reason, 'url': url},
                         extra={'spider': spider})
                log.log("3", "spider_retry_log", {'request': request.url, 'retries': retries, 'reason': str(reason), 'spider': spider.name})
            if not (retries > 3):
                # 将消息发布到kafka监听队列
                key = "{sid}:start_urls".format(sid=spider.name)
                redis_conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
                if url not in redis_conn.lrange(key, 0, -1):
                    redis_conn.rpush(key, url)
                log.log("1", "spider_retry_log", {'url': url, 'type': type, 'reason': str(reason), 'source': source})
                logger.info("push kafka for retry")
            else:
                logger.error("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
                log.log("3", "spider_retry_log", {'request': request.url, 'retries': retries, 'reason': str(reason), 'spider': spider.name})


