#!/usr/bin/env python
# coding:utf-8

import tornado.web
from service import my_service


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        ret = my_service.service_hello(0)
        self.render("../public/index.html")


class LSJHandler(tornado.web.RequestHandler):
    def post(self):
        data = open('./public/test.png').read()
        self.write(data)
        self.set_header("Content-type", "image/png")

    def get(self):
        data = open('./public/test.png').read()
        self.write(data)
        self.set_header("Content-type", "image/png")