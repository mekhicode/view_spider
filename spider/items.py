# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class CameliaItem(Item):
    # 1、概要信息
    brand = Field()
    name = Field()
    price = Field()
    stock = Field()
    discount = Field()
    is_discount = Field() # 是否是折扣单品（与discount冗余，处理不确定数据）
    sku = Field() # 商品编号
    category = Field() # 商品分类
    price_unit = Field() # 价格单位

    # 2、详细信息
    sizes = Field() # 尺码列表
    desc_product = Field() # 产品描述
    desc_size = Field() # 尺码描述
    desc_composition_care = Field() # 成分与护理描述
    desc_brand = Field() # 品牌描述
    product_code = Field() # 风格编号（在shopbop中用于库存查询）

    # 3、图片信息
    s_image_urls = Field() # 概要image信息
    d_image_urls = Field() # 详细image信息
    color_image_urls = Field() # image颜色路径信息
    image_urls = Field()
    colors = Field() # image颜色信息
    images = Field()

    # 4、数据源
    url = Field()
    s_source_url = Field()
    d_source_url = Field()
    source = Field()
    type = Field() # 类型，S: 概要信息；D: 详情信息
