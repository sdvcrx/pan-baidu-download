#!/usr/bin/env python2
#!coding=utf-8

import urllib2
import re
import sys
import os
import json
from collections import deque
import getopt
import ConfigParser

from util import bd_help


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
        self.save_vcode = int(Config().vcode)
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

    def open_in_webbrowser(self, img):
        import webbrowser
        webbrowser.open(img)

    def save(self, img):
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
            if self.save_vcode:
                self.save(img)
            else:
                self.open_in_webbrowser(img)
            input_code = raw_input("请输入看到的验证码\n")
            data = self._get_json(vcode=vcode, input_code=input_code)
            if not data.get('errno'):
                return [data.get('dlink').encode('utf-8')]
            else:
                raise VerificationCodeError

    @property
    def filename(self):
        file_pattern = re.compile(r'server_filename\\":\\"(.+?)\\"')
        filename = re.findall(file_pattern, self.data)
        filename = [fn.replace("\\\\", "\\").decode("unicode_escape").encode("utf-8") for fn in filename]
        return filename


class VerificationCodeError(Exception):
    def __str__(self):
        return '验证码错误或异常\n'


def generate_download_queue(links):
    download_queue = deque()
    for link in links:
        bd = BaiduDown(link)
        download_queue.extend(zip(bd.filename, bd.links))
    return download_queue


convert_none = lambda opt, arg: opt + arg if arg else ""


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
    print filename
    cmd = "aria2c -c -o '%s' -s5 -x5 %s %s '%s'" % (filename, convert_none('--max-download-limit=', limit),
                                                    convert_none('--dir=', output_dir), link)
    os.system(cmd)


def show(links):
    if not len(links):
        bd_help('show')
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
        self.path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'config.ini'
        self.configfile = ConfigParser.ConfigParser(allow_no_value=True)
        self.configfile.read(self.path)

    @property
    def limit(self):
        return self.configfile.get('option', 'limit')

    @limit.setter
    def limit(self, new_limit):
        self.configfile.set('option', 'limit', new_limit)
        with open(name=self.path, mode='w') as fp:
            self.configfile.write(fp)

    @property
    def dir(self):
        return self.configfile.get('option', 'dir')

    @dir.setter
    def dir(self, new_dir):
        self.configfile.set('option', 'dir', new_dir)
        with open(name=self.path, mode='w') as fp:
            self.configfile.write(fp)

    @property
    def vcode(self):
        return self.configfile.get('option', 'save_vcode')

    @vcode.setter
    def vcode(self, bol):
        self.configfile.set('option', 'save_vcode', bol)
        with open(name=self.path, mode='w') as fp:
            self.configfile.write(fp)


def config(configuration):
    cf = Config()
    if len(configuration) == 0:
        print 'limit = %s' % cf.limit
        print 'dir = %s' % cf.dir
        print 'save_vcode = %s' % cf.vcode
    elif configuration[0] == 'limit':
        cf.limit = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'dir':
        cf.dir = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'save_vcode':
        cf.vcode = configuration[1]
        print 'Saving configuration to config.ini'
    else:
        raise TypeError('修改配置错误')
    sys.exit(0)


if '__main__' == __name__:
    pass
