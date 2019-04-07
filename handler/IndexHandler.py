#!/usr/bin/env python
# coding:utf-8

import tornado.web


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
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