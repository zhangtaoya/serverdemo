#!/usr/bin/env python
# -*- coding:utf-8 -*-
import ujson
import log
from tornado import gen
from tornado.httpclient import AsyncHTTPClient


# async http call method
@gen.coroutine
def async_post(url, params=None, retjson=True, retcodesuccess=True, data=None, method='POST', headers=None,
               request_timeout=None, ensure_ascii=False):
    reqdata = ujson.dumps(params, ensure_ascii=ensure_ascii)

    # 正式环境
    try:
        http_client = AsyncHTTPClient()
        if method != 'GET':
            if data:
                response = yield http_client.fetch(url, method=method, body=data, headers=headers,
                                                   request_timeout=request_timeout)
            else:
                response = yield http_client.fetch(url, method=method, body=reqdata, headers=headers,
                                                   request_timeout=request_timeout)
        else:
            # GET method
            response = yield http_client.fetch(url, method=method, headers=headers, request_timeout=request_timeout)

    except Exception as e:
        log.error("http request error, url:%s, req:%s, e:%s" % (url, reqdata, str(e)))
        raise gen.Return({'ret': -1, 'msg': str(e)})

    # check response
    if not response:
        log.error("resp is None,url:%s, req:%s" % (url, reqdata))
        raise gen.Return({'ret': -1, 'msg': 'not response'})

    try:
        # respdata = ujson.dumps(response)
        respdata = str(response)
    except Exception as e:
        log.error("resp dump error, url:%s, req:%s, e:%s" % (url, reqdata, str(e)))
        raise gen.Return({'ret': -1, 'msg': str(e)})

    # check response code
    code = response.code
    if not code:
        log.error('resp.code is None, url:%s, req:%s, resp:%s' % (url, reqdata, respdata))
        raise gen.Return({'ret': -1, 'msg': 'resp.code is None'})
    elif (code > 400) | (code < 100):
        log.error('resp.code, url:%s, req:%s, code:%d, resp:%s' % (url, reqdata, code, respdata))
        raise gen.Return({'ret': -1, 'msg': 'code is %s' % code})
    elif code != 200:
        log.warning('resp.code, url:%s, req:%s, code:%d, resp:%s' % (url, reqdata, code, respdata))

    # check response body
    respbody = response.body
    if not respbody:
        log.error("resp.body is None, url:%s, req:%s, code:%d resp:%s" % (url, reqdata, code, respdata))
        raise gen.Return({'ret': -1, 'msg': 'resp.body is None'})

    # not check jsonformat and retcode
    if not retjson:
        raise gen.Return(respbody)

    # load response body to json
    try:
        body = ujson.loads(respbody)
        # log.info("resp.body: %s"%(ujson.dumps(body)))
        if not body:
            log.error("resp.body loads is None, url:%s, req:%s, resp:%s" % (url, reqdata, respdata))
            raise gen.Return({'ret': -1, 'msg': 'resp.body loads is None'})
    except Exception as e:
        log.warning("resp.body unmarshal error, url:%s, req:%s, respbody:%s, e:%s" % (url, reqdata, respbody, str(e)))
        raise gen.Return(respbody)

    # not check retcode success
    if not retcodesuccess:
        raise gen.Return(body)

    # get ret
    if body:
        pass
    else:
        body = dict()

    ret = body.get('ret', None)
    if not ret:
        ret = body.get('errcode', None)
        if not ret:
            body['ret'] = ret

    raise gen.Return(body)
