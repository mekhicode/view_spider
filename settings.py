# coding:utf-8

import os, sys, re
import redis

import tornado.autoreload
import tornado.httpserver
import tornado.options
import tornado.ioloop
import tornado.web

# Get parent dir as ROOT
ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(ROOT, 'views'))
sys.path.insert(0, os.path.join(ROOT, 'crontab'))
sys.path.insert(0, os.path.join(ROOT, 'static'))
sys.path.insert(0, os.path.join(ROOT, 'templates'))
sys.path.insert(0, os.path.join(ROOT, 'spider'))

from urls import url_lists
app = tornado.web.Application(
        url_lists,
        static_path=os.path.join(os.path.dirname(__file__), "static"),
)