#!/usr/bin/env python2
#!coding=utf-8

import urllib2
import re
import sys
import os
from collections import deque
from sets import Set
import getopt
import ConfigParser
import pdb

from util import bd_help


class BaiduDown(object):

    def __init__(self, raw_link):
        self.bdlink = raw_link
        self.data = self._get_download_page()

    def __repr__(self):
        return "<filename> ==> %s\n<download link> ==> %s" % (self.filename, self.links)

    def _get_download_page(self):
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)\
                    AppleWebKit/537.36 (KHTML, like Gecko)\
                    Chrome/28.0.1500.95 Safari/537.36'
        }
        request = urllib2.Request(url=self.bdlink, headers=header)
        data = urllib2.urlopen(request).read()
        return data

    @property
    def links(self):
        link_pattern = re.compile(r';;_dlink="(.+?)";')
        links = re.findall(link_pattern, self.data)
        return uniqify_list(links)

    @property
    def filename(self):
        file_pattern = re.compile(r'server_filename\\":\\"(.+?)\\"')
        filename = re.findall(file_pattern, self.data)
        filename = [fn.replace("\\\\", "\\").decode("unicode_escape").encode("utf-8") for fn in filename]
        return filename


def generate_download_queue(links):
    download_queue = deque()
    for link in links:
        bd = BaiduDown(link)
        download_queue.extend(zip(bd.filename, bd.links))
    return download_queue


def uniqify_list(seq):
    seen = Set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def download(args):
    cf = Config()
    limit = cf.dir
    output_dir = cf.dir
    optlist, links = getopt.getopt(args, 'lD', ['limit=', 'dir='])
    for k, v in optlist:
        if k == '--limit':
            limit = v
        elif k == '--dir':
            output_dir = v
    queue = generate_download_queue(links)
    while True:
        try:
            filename, link = queue.popleft()
        except IndexError:
            break
        else:
            download_command(filename, link, limit=limit, output_dir=output_dir)

    sys.exit(0)


def download_command(filename, link, limit=None, output_dir=None):
    convert_none = lambda opt, arg: opt + arg if arg else ""
    print filename
    cmd = "aria2c -c -o '%s' -s5 -x5 %s %s '%s'" % (filename, convert_none('--max-download-limit=', limit),
                                                    convert_none('--dir=', output_dir), link)
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


class Config(object):
    def __init__(self):
        self.configfile = ConfigParser.ConfigParser(allow_no_value=True)
        self.configfile.read('config.ini')


    @property
    def limit(self):
        return self.configfile.get('option', 'limit')

    @limit.setter
    def limit(self, new_limit):
        self.configfile.set('option', 'limit', new_limit)
        self.configfile.write(open('config.ini', 'w'))

    @property
    def dir(self):
        return self.configfile.get('option', 'dir')

    @dir.setter
    def dir(self, new_dir):
        self.configfile.set('option', 'dir', new_dir)
        self.configfile.write(open('config.ini', 'w'))


def config(configuration):
    cf = Config()
    if len(configuration) == 0:
        print 'limit = ', cf.limit
        print 'dir = ', cf.dir
    elif configuration[0] == 'limit':
        cf.limit = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'dir':
        cf.dir = configuration[1]
        print 'Saving configuration to config.ini'
    sys.exit(0)


if '__main__' == __name__:
    pass
