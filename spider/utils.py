# encoding: utf-8

""" 辅助方法类 """

import sys
import urllib2
import spider_logging

from PIL import Image
from StringIO import StringIO

# from fake_useragent import UserAgent

logger = spider_logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf-8')

def price_unit(price):
	""" 获取价格单位 """
	units = {
		'$': 'USD',
		'£': 'GBP',
		'¥': 'CNY',
		'€': 'EUR',
	}

	for k, v in units.items():
		if k in price:
			return k, v
	return '¥', 'CNY'

def raw_price(price, sep):
	""" 获取去除符号的价格 """
	if sep in price:
		price = price.split(sep)[1]
		return ''.join(price.split(','))
	return price

def lget(l, index):
	""" 获取list索引，忽略异常 """
	try:
		return l[index]
	except Exception, e:
		return None

def url_reader(url):
	""" 获取url内容 """
	for i in xrange(3):
		try:
			headers = {
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2799.0 Safari/537.36"
			}
			# headers = {'User-Agent': random_ua}
			req = urllib2.Request(url, headers=headers)
			res = urllib2.urlopen(req)
			data = res.read()
			res.close()
			return data
		except Exception, e:
			logger.error('---------- url reader error -----------')
			logger.error(url)
			logger.error(e)
	return None

def image_change(data):
	buffer = StringIO()
	i = Image.open(StringIO(data))
	if i.format =='JPEG':
		return data
	else:
		i.save(buffer, 'JPEG')
		return buffer.getvalue()

def image_size(data):
	""" 图片长和宽 """
	image = Image.open(StringIO(data))
	return image.size
