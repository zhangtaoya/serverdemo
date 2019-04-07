# coding=utf-8

import os

# 使用环境变量: 正式线上使用 production.py
ENV = os.environ.get('ENV', 'development')

print 'ENV: %s' % ENV

exec "from config import %s as config" % ENV

# 此条件只为了解决IDE的错误提示，不影响实际代码效果
if ENV == 'development':
    from config import development as config
else:
    from config import production as config