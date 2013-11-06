#!/usr/bin/env python2
#!coding=utf-8

import urllib2
import re
import sys
import os
import json
from collections import deque
from sets import Set

from util import bd_help


class BaiduDown(object):

    def __init__(self, raw_link):
        self.bdlink = raw_link
        self.data = self._get_download_page()
        self.filename, self.links = self._get_filename_and_link()

    def __repr__(self):
        return "<filename> ==> %s\n<download link> ==> %s" % (self.filename, self.links)

    def _get_filename_and_link(self):
        file_pattern = re.compile(r'server_filename\\":\\"(.+?)\\"')
        filename = re.findall(file_pattern, self.data)
        filename = [fn.replace("\\\\", "\\").decode("unicode_escape").encode("utf-8") for fn in filename]
        link_pattern = re.compile(r'\\"dlink\\":\\"(.*?&sh=1)')
        links = re.findall(link_pattern, self.data)
        links = [link.replace("\\", "") for link in links]
        return uniqify_list(filename), uniqify_list(links)

    def _get_download_page(self):
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)\
                    AppleWebKit/537.36 (KHTML, like Gecko)\
                    Chrome/28.0.1500.95 Safari/537.36'
        }
        request = urllib2.Request(url=self.bdlink, headers=header)
        data = urllib2.urlopen(request).read()
        return data


    #@property
    #def queue(self):
    #    download_queue = deque()
    #    download_queue.extend(zip(self.filename, self.links))
    #    return download_queue


def generate_download_queue(links):
    download_queue = deque()
    for link in links:
        bd = BaiduDown(link)
        download_queue.extend(zip(bd.filename, bd.links))
    return download_queue


def uniqify_list(seq):
    seen = Set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def download(links, limit=None, output_dir=None):
    queue = generate_download_queue(links)
    while True:
        try:
            filename, link = queue.popleft()
        except IndexError:
            break
        else:
            download_command(filename, link)

    sys.exit(0)


def download_command(filename, link, limit=None, output_dir=None):
    convert_none = lambda s: s or ""
    cmd = "aria2c -c -o '%s' -s5 -x5 %s %s '%s'" % (filename, convert_none(limit), convert_none(output_dir), link)
    os.system(cmd)


def show(links):
    if not len(links):
        bd_help(show)
    else:
        queue = generate_download_queue(links)
        while True:
            try:
                filename, link = queue.popleft()
            except IndexError:
                break
            else:
                print "%s\n%s\n\n" % (filename, link)
    sys.exit(0)


def config(argv):
    try:
        configure = json.load(file('config.json'))
        for i in configure:
            print "%-10s: %s" % (i, configure[i])
        sys.exit(0)
    except IOError, e:
        print sys.stderr >> "config.json不存在"
        print sys.stderr >> "Exception: %s" % str(e)
        sys.exit(1)


if '__main__' == __name__:
    pass
