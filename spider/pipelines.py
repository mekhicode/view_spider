# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis
import pika
import json
import datetime
from scrapy.exceptions import DropItem

from utils import price_unit, raw_price

try:
    import local_settings as settings
except Exception, e:
    import settings

# 连接池
pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

class TofoPipeline(object):
    def process_item(self, item, spider):
        return item

class ItemCleanerPipeline(object):
    """ 数据清洗 """
    def process_item(self, item, spider):
        if item.get('price', ''):
            # 格式化price，统一格式
            unit, unit_desc = price_unit(item['price'])
            item['price_unit'] = unit_desc
            item['price'] = float(raw_price(item['price'], unit).strip())
            if item.get('discount', None):
                discount = item['discount']
                discount['detail'] = dict([(color, float(raw_price(value, unit).strip())) for color, value in discount['detail'].items()])
                values = discount['detail'].values()
                discount['min'] = min(values)
                discount['max'] = max(values)
                if discount['min'] == discount['max']:
                    discount['max'] = item['price']
        return item

class ItemFilterPipeline(object):
    """ 过滤重复数据（sku+所有的price）或售罄的数据 """

    def __init__(self):
        self.r = redis.Redis(connection_pool=pool)

    def process_item(self, item, spider):
        source = item['source']
        if item.get('stock', '') == 'soldOut':
            raise DropItem("soldOut: %s-%s-%s" %(source, item['brand'], item['name']))
        sku = item['sku']
        discount = item.get('discount', {})
        fingerprint = ''.join(discount.get('detail', {}).values() + [sku])
        if self.r.sismember(source, fingerprint):
            raise DropItem("existed: %s-%s-%s" %(source, item['brand'], item['name']))
        else:
            self.r.sadd(source, fingerprint)
        return item

class ItemRabbitmqPipeline(object):

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_item(self, item, spider):
        sign = True
        try:
            message = dict(item)
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=settings.RABBIT_HOST))
            channel = connection.channel()
            message["timestamp"] = datetime.datetime.utcnow().isoformat()
            channel.queue_declare(queue='spider_queue', durable=True)
            channel.basic_publish(exchange='',
                                  routing_key='spider_queue',
                                  body=json.dumps(message),
                                  properties=pika.BasicProperties(
                                      delivery_mode = 2, # make message persistent
                                  ))
            connection.close()
        except Exception as e:
            sign = False

        if sign:
            stats = self.stats.get_stats()
            dictMerged1 = dict(dict(item).items() + stats.items())

        return item
