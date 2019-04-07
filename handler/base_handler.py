# coding=utf-8
import logging
import ujson
import socket
from datetime import datetime
from functools import wraps
import traceback
from tornado import web
from config import err, config, version
import urllib2


WHITE_ERR_MSG_LIST = [
    "shal-lite-op-spi01.in.izuiyou.com"
]


def ding_msg(cont, at=None, url_robot=None):
    try:
        url = config.url_dingding_alarm_notify
        if url_robot is not None:
            url = url_robot

        cont = {"msgtype": "text", "text": {"content": cont}, "at": {
            "atMobiles": at,
            "isAtAll": False
        }}
        hd = {'Content-Type': 'application/json'}
        req = urllib2.Request(url, ujson.dumps(cont), headers=hd)
        resp = urllib2.urlopen(req, timeout=0.5).read()
    except Exception as e:
        logging.error("ding msg failed, except:%s" % str(e))
        return False
    return True


def service_crash_alarm(url, msg):
    pass


class BaseHandler(web.RequestHandler):
    _label = 'BaseHandler'
    _app_logger = logging.getLogger('op')

    def __init__(self, application, request, **kwargs):
        web.RequestHandler.__init__(self, application, request, **kwargs)
        self.session = None
        self.user = None
        self.user_agent = None
        self.params = {}

    def head(self, *args, **kwargs):
        apply(self.get, args, kwargs)

    def prepare(self):
        if 'User-Agent' in self.request.headers:
            self.user_agent = self.request.headers['User-Agent'].lower()
            content_type = self.request.headers.get("Content-Type", '')
            if content_type.find('multipart/form-data') > -1:
                str_all = self.request.body.replace("\r\n\r\n", "\r\n")
                self.params = str_all.split("\r\n")
            else:
                if not self.request.body:
                    self.request.body = ''
                if len(self.request.body) > 1:
                    try:
                        self.params = ujson.loads(self.request.body)
                    except ValueError:
                        self.params = {}
        else:
            if not self.request.body:
                self.request.body = ''
            if len(self.request.body) > 1:
                try:
                    self.params = ujson.loads(self.request.body)
                except ValueError:
                    self.params = {}

    def on_finish(self):
        pass

    def jsonify(self, response):
        if self.session and self.session.sid:
            self.set_cookie('session', self.session.sid)
        self.set_header('Cache-Control', 'private')
        self.set_header('Date', datetime.now())
        self.set_header('Access-Control-Allow-Origin', '*')

        response = ujson.dumps(response, ensure_ascii=False)
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.write(response)
        self.finish()

    def html(self, data):
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('Date', datetime.now())
        self.set_header('Content-Type', 'text/html; charset=utf-8')
        self.write(data)
        self.finish()

    def html_response(self, template_name, cache, **kwargs):
        if cache:
            self.set_header('Cache-Control', 'public, max-age=86400')
        else:
            self.set_header('Cache-Control', 'no-cache')
        self.set_header('Date', datetime.now())
        self.set_header('Content-Type', 'text/html; charset=utf-8')

        self.render(template_name, **kwargs)

    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages.

        ``write_error`` may call `write`, `render`, `set_header`, etc
        to produce output as usual.

        If this error was caused by an uncaught exception (including
        HTTPError), an ``exc_info`` triple will be available as
        ``kwargs["exc_info"]``.  Note that this exception may not be
        the "current" exception for purposes of methods like
        ``sys.exc_info()`` or ``traceback.format_exc``.
        """

        if "exc_info" in kwargs and status_code >= 500:
            msg = "".join(traceback.format_exception(*kwargs.get("exc_info")))
            msg += "uri:%s\nbody:%s\nfrom:op_service" % (self.request.uri, self.params)
            need_notify = True
            msg += '[%s]' % socket.gethostname()
            for white in WHITE_ERR_MSG_LIST:
                if msg.find(white) >= 0:
                    need_notify = False
                    break
            if need_notify:
                service_crash_alarm(config.url_dingding_alarm_notify, msg)

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            self.finish("<html><title>%(code)d: %(message)s</title>"
                        "<body>%(code)d: %(message)s</body></html>" % {
                            "code": status_code,
                            "message": self._reason,
                        })

    @staticmethod
    def checkparamstype(params_type):
        def decorator(func):
            @wraps(func)
            def wrapper(self):
                error = False
                if isinstance(params_type, dict):
                    for k, v in params_type.items():
                        if k in self.params and not isinstance(self.params[k], v):
                            if v == int:
                                try:
                                    v(self.params[k])
                                    continue
                                except (TypeError, ValueError):
                                    pass
                            error = True
                            break
                if not error:
                    return func(self)
                ret = {'ret': err.PARAM_ERROR[0],
                       'data': {'msg': err.PARAM_ERROR[1]}}
                self.jsonify(ret)
            return wrapper
        return decorator

    @staticmethod
    def checkversion():
        def decorator(func):
            @wraps(func)
            def wrapper(self):
                web_version = self.params.get('version', '')
                ret = {'ret': err.VERSION_ERROR[0],
                       'data': {'msg': err.VERSION_ERROR[1]}}
                if not web_version or web_version < version.VERSION:
                    self.jsonify(ret)
                else:
                    return func(self)

            return wrapper
        return decorator
