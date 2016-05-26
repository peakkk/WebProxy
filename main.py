#!/usr/bin/env python
# coding: utf-8

import web
from urllib import quote
import json
import requests

urls = (
    '/(.*)', 'index',
    '(.*)', 'proxy'
)

class index(object):
    def GET(self, name=''):
        return 'hello, proxy'

class proxy(object):
    def __init__(self):
        # local proxy for shadowsocks
        self.proxies = {
            'http': 'socks5://127.0.0.1:10020/',
            'https': 'socks5://127.0.0.1:10020/'
        }

        # http-based proxy
        self.proxy_url_tpl = 'http://<IP>/proxy.php?url={}'

    def POST(self, url=''):
        return self.proxy(url)

    def GET(self, url=''):
        return self.proxy(url)

    def proxy(self, url):
        request_method = web.ctx.env.get('REQUEST_METHOD', 'GET')
        target_url = web.ctx.homedomain + '/' + web.ctx.fullpath

        # raw POST data
        data = web.data()

        # transfer cookie info
        headers = {
            'Content-Type': web.ctx.env.get('CONTENT_TYPE', None),
            'Cookie': web.ctx.env.get('HTTP_COOKIE', None),
            'User-Agent': web.ctx.env.get('HTTP_USER_AGENT', None)
        }

        for k in headers.keys():
            if headers[k] is None:
                del headers[k]

        request_method = request_method.lower()
        request_url = self.proxy_url_tpl.format(quote(target_url))

        try:
            r = getattr(requests, request_method)(request_url, data=data, headers=headers, proxies=self.proxies)
            for k in r.headers:
                # avoid some errors
                if k.lower() != 'content-encoding' and k.lower() != 'content-length':
                    web.header(k, r.headers[k])

            return r.content

        except Exception, e:
            return str(e)


if __name__ == '__main__':
    print 'Starting proxy...'
    app = web.application(urls, globals())
    app.run()