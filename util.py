#!/usr/bin/env python2
#!coding=utf-8

import bddown_help


def bd_help(args):
    if len(args) == 1:
        helper = getattr(bddown_help, args[0].lower(), bddown_help.help)
        usage(helper)
    elif len(args) == 0:
        usage(bddown_help.show_help)
    else:
        usage(bddown_help.help)


def usage(doc=bddown_help.usage, message=None):
    if hasattr(doc, '__call__'):
        doc = doc()
    if message:
        print message
    print doc.strip()

URL = ['pan.baidu.com', 'yun.baidu.com']


def check_url(raw_url=""):
    raw_url.lower()
    if raw_url.startswith('http://'):
        raw_url = raw_url[7:]
    rev = raw_url.rstrip('/').split('/')
    if rev[0] in URL and len(rev) > 1:
        return True
    return False

add_http = lambda url: url if url.startswith('http://') else 'http://'+url

