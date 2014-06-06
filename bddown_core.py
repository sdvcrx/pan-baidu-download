#!/usr/bin/env python2
# coding=utf-8
from __future__ import print_function

import re
import os
import json
import logging
import urllib2
import cookielib
from time import time

from util import convert_none
from command.config import global_config


class FileInfo(object):
    """Get necessary info from javascript code by regular expression

    Attributes:
        secret (str): the password to enter secret share page.
        bdstoken (str): token from login cookies.
        filename (list): the filenames of download files.
        fs_id (list): download files' ids.
        uk (str): user number of the share file.
        shareid (str): id of the share file.
        timestamp (str): unix timestamp of get download page.
        sign (str): relative to timestamp. Server will check sign and timestamp when we try to get download link.
    """

    def __init__(self, js):
        self.js = js
        self.info = {}
        self.filenames = []
        self.bdstoken = ""
        self.fid_list = []
        self.uk = ""
        self.shareid = ""
        self.timestamp = ""
        self.sign = ""
        self._get_info()
        self._parse_json()

    @staticmethod
    def _str2dict(s):
        return dict(
            [i.split('=', 1) for i in s.split(';') if ('File' in i or 'disk' in i) and len(i.split('=', 1)) == 2])

    def _get_info(self):
        self.info = self._str2dict(self.js[0])
        bdstoken_tmp = self._str2dict(self.js[1])
        self.info['FileUtils.bdstoken'] = bdstoken_tmp.get('FileUtils.bdstoken')
        self.shareid = self.info.get('FileUtils.share_id').strip('"')
        self.uk = self.info.get('FileUtils.share_uk').strip('"').strip('"')
        self.timestamp = self.info.get('FileUtils.share_timestamp').strip('"')
        self.sign = self.info.get('FileUtils.share_sign').strip('"')
        # self.fs_id = info.get('disk.util.ViewShareUtils.fsId').strip('"')
        self.bdstoken = self.info.get('disk.util.ViewShareUtils.bdstoken') or self.info.get(
            'FileUtils.bdstoken')
        self.bdstoken = self.bdstoken.strip('"')
        if self.bdstoken == "null":
            self.bdstoken = None
            # try:
            #     self.bdstoken = info.get('disk.util.ViewShareUtils.bdstoken').strip('"')
            # except AttributeError:
            #     self.bdstoken = info.get('FileUtils.bdstoken').strip('"')

            # TODO: md5
            # self.md5 = info.get('disk.util.ViewShareUtils.file_md5').strip('"')

    def _parse_json(self):
        # single file
        if self.js[0].startswith("var"):
            # js2 = self.js[0]
            # get json
            # [1:-1] can remove double quote
            d = [self.info.get('disk.util.ViewShareUtils.viewShareData').replace('\\\\', '\\').decode(
                "unicode_escape").replace('\\', '')[1:-1]]
        # files
        else:
            js2 = self.js[1]
            pattern = re.compile("[{]\\\\[^}]+[}]+")
            d = re.findall(pattern, js2)
            # escape
            d = [i.replace('\\\\', '\\').decode('unicode_escape').replace('\\', '') for i in d]
        d = map(json.loads, d)
        for i in d:
            # if wrong json
            if i.get('fs_id') is None:
                continue
            if i.get('isdir') == '1':
                seq = self._get_folder(i.get('path'))
                for k, j in seq:
                    self.filenames.append(k)
                    self.fid_list.append(j)
                continue
            self.fid_list.append(i.get('fs_id'))
            self.filenames.append(i.get('server_filename').encode('utf-8'))

    def _get_folder(self, path):
        # 13 digit unix timestamp
        seq = []
        t1 = int(time() * 1000)
        t2 = t1 + 6
        # interval
        tt = 1.03
        url = "http://pan.baidu.com/share/list?channel=chunlei&clienttype=0&web=1&num=100&t={t1}" \
              "&page=1&dir={path}&t={tt}d&uk={self.uk}&shareid={self.shareid}&order=time&desc=1" \
              "&_={t2}&bdstoken={self.bdstoken}".format(t1=t1, path=path, tt=tt, self=self, t2=t2)
        logging.debug(url)
        html = Pan.opener.open(url)
        j = json.load(html)
        for i in j.get('list', []):
            seq.append((i.get('server_filename'), i.get('fs_id')))
        return seq


class Pan(object):
    cookjar = cookielib.LWPCookieJar()
    if os.access(global_config.cookies, os.F_OK):
        cookjar.load(global_config.cookies)
    opener = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookjar)
    )
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0')
    ]

    def __init__(self, bdlink, secret=""):
        self.secret = secret
        self.bdlink = bdlink
        file_info = FileInfo(self._get_js())
        self.filenames = file_info.filenames
        self.bdstoken = file_info.bdstoken
        self.fid_list = file_info.fid_list
        self.uk = file_info.uk
        self.shareid = file_info.shareid
        self.timestamp = file_info.timestamp
        self.sign = file_info.sign

    def _get_js(self):
        """Get javascript code in html like '<script type="javascript">/*<![CDATA[*/  sth  /*]]>*/</script>"""
        req = self.opener.open(self.bdlink)
        if 'init' in req.url:
            self._verify_passwd(req.url)
            req = self.opener.open(self.bdlink)
        data = req.read()
        js_pattern = re.compile('<script\stype="text/javascript">/\*<!\[CDATA\[\*/(.+?)/\*\]\]>\*/</script>', re.DOTALL)
        js = re.findall(js_pattern, data)
        return js

    def _verify_passwd(self, url):
        if self.secret:
            pwd = self.secret
        else:
            pwd = raw_input("请输入提取密码\n")
        data = "pwd={0}&vcode=".format(pwd)
        url = "{0}&t={1}&".format(url.replace('init', 'verify'), int(time()))
        logging.debug(url)
        req = self.opener.open(url, data=data)
        mesg = req.read()
        logging.debug(mesg)
        logging.debug(req.info())
        errno = json.loads(mesg).get('errno')
        if errno == -63:
            raise UnknownError
        elif errno == -9:
            raise VerificationError("提取密码错误\n")

    def _get_json(self, fs_id, input_code=None, vcode=None):
        """Post fs_id to get json of real download links"""
        url = 'http://pan.baidu.com/share/download?channel=chunlei&clienttype=0&web=1' \
              '&uk={self.uk}&shareid={self.shareid}&timestamp={self.timestamp}&sign={self.sign}{bdstoken}{input_code}' \
              '{vcode}&channel=chunlei&clienttype=0&web=1'.format(self=self,
                                                                  bdstoken=convert_none('&bdstoken=', self.bdstoken),
                                                                  input_code=convert_none('&input=', input_code),
                                                                  vcode=convert_none('&vcode=', vcode))
        logging.debug(url)
        post_data = 'fid_list=["{}"]'.format(fs_id)
        logging.debug(post_data)
        req = self.opener.open(url, post_data)
        json_data = json.load(req)
        return json_data

    @staticmethod
    def save(img):
        data = urllib2.urlopen(img).read()
        with open(os.path.dirname(os.path.abspath(__file__)) + '/vcode.jpg', mode='wb') as fp:
            fp.write(data)
        print("验证码已经保存至", os.path.dirname(os.path.abspath(__file__)))

    # TODO: Cacahe support (decorator)
    # TODO: Save download status
    def _get_link(self, fs_id):
        """Get real download link by fs_id( file's id)"""
        data = self._get_json(fs_id)
        logging.debug(data)
        if not data.get('errno'):
            return data.get('dlink').encode('utf-8')
        elif data.get('errno') == -19:
            vcode = data.get('vcode')
            img = data.get('img')
            self.save(img)
            input_code = raw_input("请输入看到的验证码\n")
            data = self._get_json(fs_id, vcode=vcode, input_code=input_code)
            if not data.get('errno'):
                return data.get('dlink').encode('utf-8')
            else:
                raise VerificationError("验证码错误\n")
        else:
            raise UnknownError

    @property
    def info(self):
        fs_id = self.fid_list.pop()
        filename = self.filenames.pop()
        link = self._get_link(fs_id)
        return link, filename, len(self.fid_list)


class Album(object):
    def __init__(self, album_id, uk):
        self._album_id = album_id
        self._uk = uk
        self._limit = 100
        self._filename = []
        self._links = []
        self._get_info()

    def __len__(self):
        return len(self._links)

    def _get_info(self):
        url = "http://pan.baidu.com/pcloud/album/listfile?album_id={self._album_id}&query_uk={self._uk}&start=0" \
              "&limit={self._limit}&channel=chunlei&clienttype=0&web=1".format(self=self)
        res = Pan.opener.open(url)
        data = json.load(res)
        if not data.get('errno'):
            filelist = data.get('list')
            for i in filelist:
                # if is dir, ignore it
                if i.get('isdir'):
                    continue
                else:
                    self._filename.append(i.get('server_filename'))
                    self._links.append(i.get('dlink'))
                    # TODO: md5
                    # self._md5.append(i.get('md5'))
                    # size
                    # self._size.append(i.get('size'))
        else:
            raise UnknownError

    @property
    def info(self):
        filename = self._filename.pop()
        link = self._links.pop()
        return link, filename, len(self)


class VerificationError(Exception):
    pass


class GetFilenameError(Exception):
    pass


class UnknownError(Exception):
    pass


if __name__ == '__main__':
    pass
