#!/usr/bin/env python2
#!coding=utf-8

import urllib2
import re
import sys
import os
import json
from collections import deque
from sets import Set

from bddown_help import command_help


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


def generate_download_queue(links):
    link_queue = deque()
    filename_queue = deque()
    for link in links:
        bd = BaiduDown(link)
        link_queue.extend(bd.links)
        filename_queue.extend(bd.filename)

    download_queue = deque(zip(filename_queue, link_queue))
    while True:
        try:
            filename, link = download_queue.popleft()
        except IndexError:
            print "Download Complete!"
            break
        else:
            download(link, filename)

    sys.exit(0)


def uniqify_list(seq):
    seen = Set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def download(link, filename, limit=None):
    if limit:
        cmd = "aria2c -c -o '%s' -s5 -x5 %s '%s'" % (filename, limit, link)
    else:
        cmd = "aria2c -c -o '%s' -s5 -x5 '%s'" % (filename, link)
    os.system(cmd)


def show(links):
    if not len(links):
        print command_help['show']
    for link in links:
        bd = BaiduDown(link)
        print bd.filename, '\n', bd.links, '\n'
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
