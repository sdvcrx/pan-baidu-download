#!/usr/bin/env python2
# coding=utf-8

import bddown_help

__all__ = [
    "bd_help",
    "usage",
    "check_url",
    "add_http",
    "convert_none",
    "bcolor",
    "in_list",
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
        print message
    print doc.strip()


def check_url(raw_url=""):
    raw_url.lower()
    if raw_url.startswith('http://'):
        raw_url = raw_url[7:]
    rev = raw_url.rstrip('/').split('/')
    if rev[0] in URL and len(rev) > 1:
        return True
    return False

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
