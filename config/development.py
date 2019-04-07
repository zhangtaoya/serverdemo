# coding=utf-8

"""生产环境使用的配置
"""
from config.base import *
WEB_DEBUG = False

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = "iuasn8293"

'''
DB_HOST = "mongodb://172.16.255.176:27047/?replicaSet=opr"
DB_PORT = 29017
'''

DB_HOST = "127.0.0.1"
DB_PORT = 29017

DB_MINE_HOST = "127.0.0.1"
DB_MINE_PORT = 29017
