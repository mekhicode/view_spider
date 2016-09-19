# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import tornado.web
import redis
import re
from tornado.web import RequestHandler
import json
import sys
sys.path.append("..")
from view_spider.spider import crawler
from base import BaseHandler


TIMEOUT = 86400
redis_conn = redis.Redis(host='localhost', port=6379)

class Search(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.render("../templates/main.html", title="My title")

    def post(self, *args, **kwargs):
        for i in self.request.arguments:
            print i
            print self.get_arguments(i)
        keyword = self.get_argument("keyword")
        key = "{sid}:start_urls".format(sid="tofo")
        redis_conn.rpush(key, "https://tofo.me/" + keyword)
        crawler.start()
        # post_data = {}
        # for key in self.request.arguments:
        #     post_data[key] = self.get_arguments(key)
        # self.write(json.dumps(results))


class SubPlugin(BaseHandler):
    def post(self, *args, **kwargs):
        url = self.get_argument("url")
        if "shopbop" in url:
            if url:
                response = {"result": u"网站正在抓取,请耐心等候,如果有技术问题,请联系技术!"}
                crawler.start_other([url])
                # gevent.spawn(crawler.start_other([url])).join()
            else:
                response = {"result": u"网站抓取失败,请联系技术反馈问题!"}
        else:
            response = {"result": u"网站还未收录,请反馈给技术!"}
        print response
        self.write(response)
        # crawler.start_other([url])
        # post_data = {}
        # for key in self.request.arguments:
        #     post_data[key] = self.get_arguments(key)
