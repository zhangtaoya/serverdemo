#!/usr/bin/env python
# coding:utf-8

from service import my_service
from base_handler import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        ret = my_service.service_hello(0)
        self.render("../public/index.html")


class LSJHandler(BaseHandler):
    def post(self):
        data = open('./public/test.png').read()
        self.write(data)
        self.set_header("Content-type", "image/png")

    def get(self):
        data = open('./public/test.png').read()
        self.write(data)
        self.set_header("Content-type", "image/png")