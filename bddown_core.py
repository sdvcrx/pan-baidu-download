#!/usr/bin/env python2
#!coding=utf-8

import urllib2
import re


class BaiduDown(object):

    def __init__(self, bdlink):
        self.bdlink = bdlink
        self.data = self._get_download_page()
        self.filename, self.link = self._get_filename_and_link()

    def __repr__(self):
        return "<filename> ==> %s\n<download link> ==> %s" % (self.filename, self.link)

    def _get_filename_and_link(self):
        file_pattern = re.compile(r'var\sserver_filename="(.+?)"')
        filename = re.search(file_pattern, self.data).group(1)
        link_pattern = re.compile(r'\\"dlink\\":\\"(.*?&sh=1)')
        link = re.search(link_pattern, self.data).group(1).replace('\\', '')
        return (filename, link)

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

if '__main__' == __name__:
    bd = BaiduDown(r'http://pan.baidu.com/s/17mIrW')
    print bd.link, bd.filename