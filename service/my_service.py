# -*- coding:utf-8 -*-
import sys

from tornado import gen

from lib.db import *

reload(sys)
sys.setdefaultencoding('utf-8')


@gen.coroutine
def service_hello(phone):
    col = get_col_test_my()
    raise gen.Return({'ret':1, 'ph': phone})
