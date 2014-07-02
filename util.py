#!/usr/bin/env python2
# coding=utf-8
from __future__ import print_function

import urlparse
import logging

import bddown_help

__all__ = [
    "bd_help",
    "usage",
    "parse_url"
    "add_http",
    "convert_none",
    "bcolor",
    "in_list",
    "logger",
]

URL = ['pan.baidu.com', 'yun.baidu.com']
FILTER_KEYS = ['shareid', 'server_filename', 'isdir', 'fs_id', 'sign', 'time_stamp', 'shorturl', 'dlink',
               'filelist', 'operation']
# TODO: add md5


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
        print(message)
    print(doc.strip())


def parse_url(url):
    """
    This function will parse url and judge which type the link is.

    :type url: str
    :param url: baidu netdisk share url.
    :return: dict
    """
    result = urlparse.urlparse(url)

    # wrong url
    if result.netloc not in ('pan.baidu.com', 'yun.baidu.com'):
        return {'type': -1}

    # http://pan.baidu.com/s/1kTFQbIn or http://pan.baidu.com/share/link?shareid=2009678541&uk=2839544145
    if result.path.startswith('/s/') or ('link' in result.path):
        return {'type': 1}

    # http://pan.baidu.com/share/verify?shareid=2009678541&uk=2839544145
    elif 'init' in result.path:
        return {'type': 1}

    # http://pan.baidu.com/pcloud/album/info?uk=3943531277&album_id=1553987381796453514
    elif 'album' in result.path:
        info = dict(urlparse.parse_qsl(result.query))
        info['type'] = 2
        return info

    # TODO: download share home
    # http://pan.baidu.com/share/home?uk=NUMBER
    elif 'home' in result.path and result.query:
        return {'type': 3}
    else:
        return {'type': 0}

add_http = lambda url: url if url.startswith('http://') else 'http://'+url

convert_none = lambda opt, arg: opt + arg if arg else ""


# from http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
# THANKS!

class BColor(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

bcolor = BColor()

in_list = lambda key, want_keys: key in want_keys


def filter_dict(bool_func, dictionary, want_keys):
    filtered_dict = {}
    for each_key in dictionary.keys():
        if bool_func(each_key, want_keys):
            filtered_dict[each_key] = dictionary[each_key]
    return filtered_dict


def merge_dict(dictionary, key):
    # will remove
    try:
        dictionary.update(dictionary[key][0])
        del dictionary[key]
    except KeyError:
        pass
    return dictionary


def filter_dict_wrapper(dictionary):
    d = {}
    for (k, v) in dictionary.items():
        if k in FILTER_KEYS:
            d[k] = v
        elif k == 'filelist':
            d[k] = [filter_dict(in_list, item, FILTER_KEYS) for item in v]
        elif k == 'operation':
            d[k] = [filter_dict(in_list, item, FILTER_KEYS) for item in v[0].get('filelist')]
    return d


def get_logger(logger_name):
    alogger = logging.getLogger(logger_name)
    fmt = logging.Formatter("%(levelname)s - %(method)s - %(type)s: \n-> %(message)s\n")
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    alogger.addHandler(handler)
    alogger.setLevel(logging.INFO)
    return alogger


logger = get_logger('pan')
