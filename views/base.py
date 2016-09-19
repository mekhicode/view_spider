# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from tornado.web import RequestHandler

class BaseHandler(RequestHandler):
    def set_default_headers(self):
        """ 跨域请求 """
        self.set_header("Access-Control-Allow-Origin", "*")

    def prepare(self):
        """ 完成request之前的准备工作 """
        remote_ip = self.request.remote_ip
        print remote_ip

    def get_current_user(self):
        return self.get_secure_cookie("user")