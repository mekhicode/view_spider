# encoding: utf-8
import json
import urlparse
import pika
import scrapy
from utils import price_unit, raw_price
import settings
import datetime
from items import CameliaItem
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
import redis


class TofoSpider(RedisSpider):
    name = 'tofo'
    MAX_PAGE = 10
    allowed_domain = ["https://tofo.me/"]
    start_urls = []

    def parse(self, response):
        iChardet = response.encoding if hasattr(response, 'encoding') else chardet.detect(response.body)['encoding']
        html = response.body.decode(iChardet,"ignore")
        hxs = Selector(text=html, type="html")
        print "=======spider=========="
        # print hxs.xpath('//div[@class="profile-username"]/span[1]/text()').extract_first()
        init_data = hxs.xpath('//script[@type="text/javascript"]/text()').extract_first().strip()
        init_data = init_data.split('window.ctxData = ')[-1][:-1]
        print init_data
        self.finish_crawl(response.url)

    def next_parse(self, response):
        iChardet = response.encoding if hasattr(response, 'encoding') else chardet.detect(response.body)['encoding']
        html = response.body.decode(iChardet,"ignore")
        hxs = Selector(text=html, type="html")
        pass

    def finish_crawl(self, url):
        import time
        time.sleep(10)
        redis_conn = redis.Redis(host='localhost', port=6379)
        key = "{sid}:start_urls".format(sid=self.name)
        if url not in redis_conn.lrange(key, 0, -1):
            redis_conn.rpush(key, url)




base_url = "https://cn.shopbop.com"
source = 'shopbop'

categories = {
    'clothing': '服装',
    'shoes': '鞋履',
    'bags': '包袋',
    'accessories': '配饰',
}

def category_getter(url):
    """ 根据url获取单品分类信息 """
    for k, v in categories.items():
        if k in url:
            return v
    return 'unknown'

def image_url_splitter(url, sep='_p1_'):
    """ 根据指定字符串分割图片路径 """
    if sep in url:
        idx = url.rindex(sep)
        return url[:idx], url[idx+len(sep):]
    else:
        for sep in ['_p2_', '_p3_', '_p4_', '_p5_']:
            if sep in url:
                idx = url.rindex(sep)
                return url[:idx], url[idx+len(sep):]

def price_formatter(price):
    """ price 格式化 """
    price = price.strip()
    splitted_price = price.split()
    if len(splitted_price) == 2:
        return ''.join(splitted_price)
    else:
        return price


class ShopbopTempSpider(scrapy.Spider):
    name = 'shopboptemp'
    MAX_PAGE = 50
    allowed_domain = ["shopbop.com"]
    # start_urls = [
    #     # 'https://cn.shopbop.com/actions/viewSearchResultsAction.action?searchButton=%E6%8F%90%E4%BA%A4&query=Donald&searchSuggestion=false',
    # ]
    def __init__(self, url, *args, **kwargs):
        super(ShopbopTempSpider, self).__init__(*args, **kwargs)
        print url
        self.start_urls = url

    def parse(self, response):
        """ 默认爬虫调用方法 """
        # log.log("1", "spider_base_start", {"name": self.name})
        for item_or_request in self.safe_parse(response):
            yield item_or_request

    def parse_listing_items(self, response):
        """ 处理产品概要信息 """
        # 获取单品分类
        category = category_getter(response.url)
        # 获取概要信息列表
        listing_items = response.xpath('//ul[@id="product-container"]/li')
        for item in listing_items:
            meta = {'category': category}
            # 获取单品编号
            sku = item.xpath('@data-productid').extract_first()
            meta['sku'] = sku
            # 获取单品信息
            content = item.xpath('div/div[@class="info clearfix"]')
            detail_link = content.xpath('a/@href').extract_first()

            # 单品来源
            meta['s_source_url'] = response.request.url
            if detail_link:
                detail_link = urlparse.urljoin(base_url, detail_link)
                yield scrapy.Request(detail_link, self.parse_item_detail, meta=meta)

    def parse_item_detail(self, response):
        """ 处理产品详情 """
        meta = response.meta
        cs_item = CameliaItem()
        cs_item['sku'] = response.meta['sku']
        # 获取详情信息列表
        product = response.xpath('//div[@id="product-information"]')
        # 1、获取详情信息
        cs_item['brand'] = product.xpath('h1/.//a/text()').extract_first().strip()
        cs_item['name'] = product.xpath('h1/span/text()').extract_first().strip()
        prices = product.xpath('div[@id="productPrices"]/div[@class="priceBlock"]')
        if len(prices) > 1:
            # 包含原价与折扣
            price = prices[0].xpath('span/text()').extract_first().strip()
            if ':' in price:
                price = price.split(':')[0]
            sale_prices = prices.xpath('span[@class="salePrice"]/text() | span[@class="regularPrice"]/text()').extract()
            sale_prices = map(lambda x: x.split(':')[0], sale_prices)
            price_colors = prices.xpath('span[@class="priceColors"]/text()').extract()
            # 处理统一价格多种颜色的情况，如：黑色，白色：$151
            detail = {}
            for i in range(len(price_colors)):
                if ',' in price_colors[i]:
                    for price_color in price_colors[i].split(','):
                        detail[price_color.strip()] = sale_prices[i]
                else:
                    detail[price_colors[i].strip()] = sale_prices[i]

            cs_item['discount'] = {
                'type': 'color',
                'detail': detail,
            }
            cs_item['is_discount'] = True

        else:
            cs_item['is_discount'] = False
            cs_item['discount'] = {}
            price = prices[0].xpath('text()').extract_first().strip()

        cs_item['price'] = price

        # 2、获取尺码信息（js....）
        cs_item['sizes'] = []
        sizes = product.xpath('.//div[@id="sizes"]/span[@class="size hover"]')
        for size in sizes:
            size_id = size.xpath('@id').extract_first()
            size_name = size.xpath('text()').extract_first()
            size_dict = {'id': size_id, 'name': size_name}
            cs_item['sizes'].append(size_dict)

        # 3、描述信息
        details = response.xpath('//div[@id="detailsAccordion"]')
        # desc = details.xpath('.//div[@itemprop="description"]/text()').extract_first()
        desc = details.xpath('.//div[@itemprop="description"]')
        desc = desc.xpath('string(.)').extract()[0].strip()
        if u"这件物品不能运送到美国境外" in desc:
            print "find page"
            return
        desc = desc.split(u"尺寸")
        cs_item['desc_product'] = desc[0]
        cs_item['desc_size'] = desc[-1]

        # 6、品牌信息
        cs_item['desc_brand'] = ''

        color_image_urls, colors, cs_item['d_image_urls'], d_image_urls = [], [], [], []
        productDetail = response.xpath('//script[contains(text(),"productDetail")]/text()').extract()
        for i in productDetail:
            if i:
                i = i.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '').split('}};')[0][17:] + '}}'
                info = json.loads(i)['colors']
                for k, v in info.items():
                    temp = {}
                    temp['id'] = v['color']
                    temp['name'] = v['colorName']
                    color_image_urls.append(v['swatch'])
                    colors.append(temp)
                    image_urls = []
                    for image, imagename in v['images'].items():
                        image_urls.append(imagename['zoom'])
                    image_urls.sort()
                    d_image_urls.append(image_urls)
                    cs_item['d_image_urls'] = d_image_urls
                    cs_item['color_image_urls'] = color_image_urls
                    cs_item['colors'] = colors

        if cs_item['is_discount']:
            discount = cs_item['discount']['detail']
            colors = cs_item['colors']
            if len(discount) != len(colors):
                for i in colors:
                    if i['name'] not in discount:
                        cs_item['discount']['detail'][i['name']] = cs_item['price']
        # 8、单品来源
        cs_item['source'] = source
        cs_item['d_source_url'] = response.request.url

        # 9、获取风格编号
        product_code = response.xpath('//span[@id="productCode"]/text()').extract_first()
        cs_item['product_code'] = product_code

        # 追加概要信息
        cs_item['category'] = meta['category']
        cs_item['sku'] = meta['sku']
        cs_item['s_source_url'] = meta['s_source_url']

        data = self.itemCleaner(cs_item)
        self.itemRabbitmq(data)
        # yield cs_item


    def safe_parse(self, response):

        for item_or_request in self.parse_listing_items(response):
            yield item_or_request

        # 获取下一页地址
        next_url = response.xpath('//span[@class="next"]/@data-next-link').extract()
        if next_url:
            next_url = urlparse.urljoin(base_url, next_url[0])
            yield scrapy.Request(next_url, callback=self.safe_parse)

    def itemCleaner(self, item):
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

    def itemRabbitmq(self, item):
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
            print e