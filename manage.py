# coding:utf-8

import tornado.autoreload
import tornado.httpserver
import tornado.options
import tornado.ioloop
import tornado.web

from settings import app

app.listen(8008)
tornado.options.parse_command_line()
http_server = tornado.httpserver.HTTPServer(app)
instance = tornado.ioloop.IOLoop.instance()
tornado.autoreload.start(instance)

try:
    instance.start()
except:
    instance.stop()