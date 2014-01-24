#!/usr/bin/env python2
#!coding=utf-8

import urllib2
import re
import sys
import os
import json
from collections import deque
import getopt

from util import bd_help
from command.config import configure


class BaiduDown(object):
    def __init__(self, raw_link):
        self.bdlink = raw_link
        self.header = {
            'Host': 'pan.baidu.com',
            'Origin': 'http://pan.baidu.com',
            'Referer': self.bdlink,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)\
                    AppleWebKit/537.36 (KHTML, like Gecko)\
                    Chrome/28.0.1500.95 Safari/537.36'
        }
        self.data = self._get_download_page()
        self.fid_list, self.share_uk, self.share_id, self.timestamp, self.sign = self._get_info()

    def __repr__(self):
        return "<filename> ==> %s\n<download link> ==> %s" % (self.filename, self.links)

    def _get_download_page(self):
        request = urllib2.Request(url=self.bdlink, headers=self.header)
        data = urllib2.urlopen(request).read()
        return data

    def _get_info(self):
        status = True
        fid_pattern = re.compile(r'disk.util.ViewShareUtils.fsId="(.+?)"', re.DOTALL)
        try:
            fid_list = re.findall(fid_pattern, self.data)[0]
        except IndexError:
            status = False
        pattern = re.compile(r'FileUtils.share_uk="(\d+)";FileUtils.share_id="(\d+)";.+?;'
                             r'FileUtils.share_timestamp="(\d+)";FileUtils.share_sign="(.+?)"', re.DOTALL)
        try:
            info = re.findall(pattern, self.data)[0]
            share_uk, share_id, timestamp, sign = info
        except IndexError:
            status = False
        if status:
            return fid_list, share_uk, share_id, timestamp, sign
        else:
            return None, None, None, None, None

    def _get_json(self, input_code=None, vcode=None):
        url = 'http://pan.baidu.com/share/download?channel=chunlei&clienttype=0&web=1' \
              '&uk=%s&shareid=%s&timestamp=%s&sign=%s&fid_list=["%s"]%s%s' \
              '&channel=chunlei&clienttype=0&web=1' % \
              (self.share_uk, self.share_id, self.timestamp, self.sign, self.fid_list,
               convert_none('&input=', input_code),
               convert_none('&vcode=', vcode))
        req = urllib2.Request(url=url, headers=self.header)
        json_data = json.load(urllib2.urlopen(req))
        return json_data

    @staticmethod
    def save(img):
        data = urllib2.urlopen(img).read()
        with open(os.path.dirname(os.path.abspath(__file__)) + '/vcode.jpg', mode='wb') as fp:
            fp.write(data)
        print "验证码已经保存至", os.path.dirname(os.path.abspath(__file__))

    @property
    def links(self):
        data = self._get_json()
        if not data.get('errno'):
            return [data.get('dlink').encode('utf-8')]
        else:
            vcode = data.get('vcode')
            img = data.get('img')
            self.save(img)
            input_code = raw_input("请输入看到的验证码\n")
            data = self._get_json(vcode=vcode, input_code=input_code)
            if not data.get('errno'):
                return [data.get('dlink').encode('utf-8')]
            else:
                raise VerificationCodeError("验证码错误\n")

    @property
    def filename(self):
        file_pattern = re.compile(r'server_filename\\":\\"(.+?)\\"')
        filename = re.findall(file_pattern, self.data)
        filename = [fn.replace("\\\\", "\\").decode("unicode_escape").encode("utf-8") for fn in filename]
        return filename


class VerificationCodeError(Exception):
    pass


def generate_download_queue(links):
    download_queue = deque()
    for link in links:
        bd = BaiduDown(link)
        download_queue.extend(zip(bd.filename, bd.links))
    return download_queue


convert_none = lambda opt, arg: opt + arg if arg else ""


def download(args):
    limit = configure.limit
    output_dir = configure.dir
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
    print "\033[32m" + filename + "\033[0m"
    firefox_ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'
    cmd = "aria2c -c -o '%(filename)s' -s5 -x5" \
          " --user-agent='%(useragent)s' --header 'Referer:http://pan.baidu.com/disk/home'" \
          " %(limit)s %(dir)s '%(link)s'" % {
              "filename": filename,
              "useragent": firefox_ua,
              "limit": convert_none('--max-download-limit=', limit),
              "dir": convert_none('--dir=', output_dir),
              "link": link
          }
    os.system(cmd)

if '__main__' == __name__:
    pass
