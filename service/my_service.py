# -*- coding:utf-8 -*-
import time
import random
import urllib2
import ujson
from tornado import gen
from lib import motordb
from lib import call
from lib.db import get_redis
from lib.db import *
from config import config
import log
import hashlib
import time
import random
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


TTL_VERIFY_CODE = 182
TTL_NONCE = 7 * 24 * 3600


@gen.coroutine
def service_hello(phone):
    col = get_col_test_my()
    raise gen.Return({'ret':1, 'ph': phone})
