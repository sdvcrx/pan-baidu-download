#!/usr/bin/env python2
#!coding=utf-8

import cookielib
import urllib2
import re
import sys
import os
import subprocess
import json
import getopt
import logging
from time import time

from util import check_url, add_http
from command.config import global_config


class BaiduDown(object):
    def __init__(self, raw_link, secret=None):
        self.bdlink = raw_link
        self.secret = secret
        self.cookjar = cookielib.LWPCookieJar()
        if os.access(configure.cookies, os.F_OK):
            self.cookjar.load(configure.cookies)
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookjar)
        )
        self.opener.addheaders = [
            ('Referer', self.bdlink),
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')
        ]
        self.data = self._get_download_page()
        self.fid_list, self.share_uk, self.share_id, self.timestamp, self.sign = self._get_info()

    def _get_download_page(self):
        req = self.opener.open(self.bdlink)
        if 'init' in req.url:
            self._verify_passwd(req.url)
            req = self.opener.open(self.bdlink)
        data = req.read()
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
        req = self.opener.open(url)
        json_data = json.load(req)
        return json_data

    def _verify_passwd(self, url):
        if self.secret is not None:
            pwd = self.secret
        else:
            pwd = raw_input("请输入提取密码\n")
        data = "pwd=%s&vcode=" % pwd
        url = "%s&t=%d&" % (url.replace('init', 'verify'), int(time()))
        logging.debug(url)
        req = self.opener.open(url, data=data)
        mesg = req.read()
        logging.debug(mesg)
        logging.debug(req.info())
        errno = json.loads(mesg).get('errno')
        if errno == -63:
            self._vcode_handle()
        elif errno == -9:
            raise VerificationError("提取密码错误\n")

    # TODO
    def _vcode_handle(self):
        raise VerificationError("检测到需要输入验证码，建议稍后再试\n")

    @staticmethod
    def save(img):
        data = urllib2.urlopen(img).read()
        with open(os.path.dirname(os.path.abspath(__file__)) + '/vcode.jpg', mode='wb') as fp:
            fp.write(data)
        print "验证码已经保存至", os.path.dirname(os.path.abspath(__file__))

    @property
    def link(self):
        data = self._get_json()
        if not data.get('errno'):
            return data.get('dlink').encode('utf-8')
        else:
            vcode = data.get('vcode')
            img = data.get('img')
            self.save(img)
            input_code = raw_input("请输入看到的验证码\n")
            data = self._get_json(vcode=vcode, input_code=input_code)
            if not data.get('errno'):
                return data.get('dlink').encode('utf-8')
            else:
                raise VerificationError("验证码错误\n")

    @property
    def filename(self):
        file_pattern = re.compile(r'server_filename\\":\\"(.+?)\\"')
        try:
            filename = re.search(file_pattern, self.data).group(1)
            filename = filename.replace("\\\\", "\\").decode("unicode escape").encode("utf-8")
        except AttributeError:
            raise GetFilenameError("无法获取文件名")
        return filename


class VerificationError(Exception):
    pass


class GetFilenameError(Exception):
    pass


convert_none = lambda opt, arg: opt + arg if arg else ""


def download(args):
    optlist, links = getopt.getopt(args, 'lDS', ['limit=', 'dir=', 'secret='])
    secret = None
    limit = global_config.limit
    output_dir = global_config.dir
    for k, v in optlist:
        if k == '--limit':
            limit = v
        elif k == '--dir':
            output_dir = os.path.expanduser(v)
        elif k == '--secret':
            secret = v
    links = filter(check_url, links)    # filter the wrong url
    links = map(add_http, links)        # add 'http://'
    for url in links:
        pan = BaiduDown(url, secret)
        filename = pan.filename
        link = pan.link
        download_command(filename, link, limit=limit, output_dir=output_dir)

    sys.exit(0)


def download_command(filename, link, limit=None, output_dir=None):
    bool(output_dir) and not os.path.exists(output_dir) and os.makedirs(output_dir)
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
    subprocess.call(cmd, shell=True)

if '__main__' == __name__:
    pass
