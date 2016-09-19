# coding:utf-8

from views import main

url_lists = [
    (r'/', main.Search),
    (r'/test', main.SubPlugin),
]