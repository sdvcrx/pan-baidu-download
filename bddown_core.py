#!/usr/bin/env python2
#!coding=utf-8

import urllib2
import re
import sys
import os
import json

from bddown_help import command_help


class BaiduDown(object):

    def __init__(self, raw_link):
        self.bdlink = raw_link
        self.data = self._get_download_page()
        self.filename, self.link = self._get_filename_and_link()

    def __repr__(self):
        return "<filename> ==> %s\n<download link> ==> %s" % (self.filename, self.link)

    def _get_filename_and_link(self):
        file_pattern = re.compile(r'var\sserver_filename="(.+?)"')
        filename = re.search(file_pattern, self.data).group(1)
        link_pattern = re.compile(r'\\"dlink\\":\\"(.*?&sh=1)')
        link = re.search(link_pattern, self.data).group(1).replace('\\', '')
        return filename, link

    def _get_download_page(self):
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)\
                    AppleWebKit/537.36 (KHTML, like Gecko)\
                    Chrome/28.0.1500.95 Safari/537.36'
        }
        request = urllib2.Request(url=self.bdlink, headers=header)
        data = urllib2.urlopen(request).read()
        script_pattern = re.compile(r'<script type="text/javascript">(.+?)</script>', re.DOTALL)
        script = re.findall(script_pattern, data)[2]
        return script


def download(links, limit=None):
    for link in links:
        bd = BaiduDown(link)
        if not limit:
            cmd = "aria2c -c -o '%s' -s5 -x5 %s '%s'" % (bd.filename, limit, bd.link)
        else:
            cmd = "aria2c -c -o '%s' -s5 -x5 '%s'" % (bd.filename, bd.link)
        os.system(cmd)
    sys.exit(0)


def show(links):
    if not len(links):
        print command_help['show']
    for link in links:
        bd = BaiduDown(link)
        print bd.filename, '\n', bd.link, '\n'
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