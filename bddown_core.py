#!/usr/bin/env python2
# coding=utf-8
from __future__ import print_function

import re
import os
import json
import pickle
from time import time

import requests

from util import convert_none, logger
from command.config import global_config

BAIDUPAN_SERVER = "http://pan.baidu.com/"


class Pan(object):
    headers = {}

    def __init__(self):
        self.baiduid = ''
        self.bduss = ''
        self.bdstoken = ''
        self.session = requests.Session()
        self.cookies = self.session.cookies

    def _load_cookies_from_file(self):
        """Load cookies file if file exist."""
        if os.access(global_config.cookies, os.F_OK):
            with open(global_config.cookies) as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
            self.session.cookies = cookies
            # NOT SURE stoken is bdstoken!
            # self.token = self.session.cookies.get('STOKEN')
            self.baiduid = self.cookies.get('BAIDUID')
            self.bduss = self.cookies.get('BDUSS')
            return True
        return False

    @staticmethod
    def _str2dict(s):
        """Try convert javascript variable to dict and return the dict."""
        return dict(
            [i.split('=', 1) for i in s.split(';') if ('File' in i or 'disk' in i) and len(i.split('=', 1)) == 2])

    def _save_img(self, img_url):
        """Download vcode image and save it to path of source code."""
        r = self.session.get(img_url)
        data = r.content
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vcode.jpg')
        with open(img_path, mode='wb') as fp:
            fp.write(data)
        print("Saved verification code to ", os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def _dict_to_utf8(dictionary):
        """Convert dictionary's value to utf-8"""
        if not isinstance(dictionary, dict):
            return
        for k, v in dictionary.items():
            if isinstance(v, unicode):
                dictionary[k] = v.encode('utf-8')

    def verify_passwd(self, url, secret=None):
        """
        Verify password if url is a private sharing.
        :param url: link of private sharing. ('init' must in url)
        :type url: str
        :param secret: password of the private sharing
        :type secret: str
        :return: None
        """
        if secret:
            pwd = secret
        else:
            # FIXME: Improve translation
            pwd = raw_input("Please input this sharing password\n")
        data = {'pwd': pwd, 'vcode': ''}
        url = "{0}&t={1}&".format(url.replace('init', 'verify'), int(time()))
        logger.debug(url, extra={'type': 'url', 'method': 'POST'})
        r = self.session.post(url=url, data=data, headers=self.headers)
        mesg = r.json
        logger.debug(mesg, extra={'type': 'JSON', 'method': 'POST'})
        errno = mesg.get('errno')
        if errno == -63:
            raise UnknownError
        elif errno == -9:
            raise VerificationError("提取密码错误\n")

    def request(self, method='GET', base_url='', extra_params=None, post_data=None, **kwargs):
        """
        Send a request based on template.
        :param method: http method, GET or POST
        :param base_url: base url
        :param extra_params: extra params for url
        :type extra_params: dict
        :param post_data: post data. Ignore if method is GET
        :type post_data: dict
        :return: requests.models.Response or None if invainvalid
        """
        params = {
            'channel': 'chunlei',
            'clienttype': 0,
            'web': 1,
            'app_id': 250528,
            't': str(int(time())),
            'bdstoken': self.cookies.get('STOKEN')
        }
        if isinstance(extra_params, dict):
            params.update(extra_params)
            self._dict_to_utf8(params)
        if method == 'GET' and base_url:
            response = self.session.get(base_url, params=params, headers=self.headers, **kwargs)
        elif method == 'POST' and base_url and post_data:
            response = self.session.post(base_url, data=post_data, params=params, headers=self.headers, **kwargs)
        else:
            response = None
        return response


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

    def _get_info(self):
        self.info = self._str2dict(self.js[0])
        try:
            bdstoken_tmp = self._str2dict(self.js[1])
        except IndexError:
            raise DownloadError("The share link has been deleted!")
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
        """Try parse json from javascript code."""
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
        log_message = {'method': 'GET', 'type': 'url'}
        logger.debug(url, extra=log_message)
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

    def _get_json(self, fs_id, input_code=None, vcode=None):
        """Post fs_id to get json of real download links"""
        url = 'http://pan.baidu.com/share/download?channel=chunlei&clienttype=0&web=1' \
              '&uk={self.uk}&shareid={self.shareid}&timestamp={self.timestamp}&sign={self.sign}{bdstoken}{input_code}' \
              '{vcode}&channel=chunlei&clienttype=0&web=1'.format(self=self,
                                                                  bdstoken=convert_none('&bdstoken=', self.bdstoken),
                                                                  input_code=convert_none('&input=', input_code),
                                                                  vcode=convert_none('&vcode=', vcode))
        log_message = {'type': 'url', 'method': 'POST'}
        logger.debug(url, extra=log_message)
        post_data = 'fid_list=["{}"]'.format(fs_id)
        log_message = {'type': 'post data', 'method': 'POST'}
        logger.debug(post_data, extra=log_message)
        req = self.opener.open(url, post_data)
        json_data = json.load(req)
        return json_data

    def _get_home_file_dlink(self, fs_id, sign):
        """Post fs_id to get home file dlink"""
        url = 'http://pan.baidu.com/api/download?channel=chunlei&clienttype=0&web=1&app_id=250528' \
              '{bdstoken}'.format(bdstoken=convert_none("&bdstoken=", self.bdstoken))
        log_message = {'type': 'url', 'method': 'POST'}
        logger.debug(url, extra=log_message)
        post_data = 'fidlist=[{fs_id}]&timestamp={t}&sign={sign}' \
                    '&type=dlink'.format(fs_id=fs_id, sign=sign, t=str(int(time())))
        log_message = {'type': 'post data', 'method': 'POST'}
        logger.debug(post_data, extra=log_message)
        req = self.opener.open(url, post_data)
        json_data = json.load(req)
        return json_data

    # TODO: Cacahe support (decorator)
    # TODO: Save download status
    def _get_link(self, fs_id):
        """Get real download link by fs_id( file's id)"""
        data = self._get_json(fs_id)
        log_message = {'type': 'JSON', 'method': 'GET'}
        logger.debug(data, extra=log_message)
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
        """Get album's files info which has filename and download link. (And md5, file size)"""
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


class DownloadError(Exception):
    pass


if __name__ == '__main__':
    pass
