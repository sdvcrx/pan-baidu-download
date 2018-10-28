#!/usr/bin/env python2
# coding=utf-8
from __future__ import print_function

import re
import os
import json
import platform
import pickle
from time import time
try:
    from urllib import unquote as url_unquote
except ImportError:
    from urllib.parse import unquote as url_unquote

import requests

import util
from util import logger
from command.config import global_config

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

BAIDUPAN_SERVER = "http://pan.baidu.com/api/"
VCODE = 'vcode.jpg'


class Pan(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/37.0.2062.120 Safari/537.36'
    }

    def __init__(self):
        self.baiduid = ''
        self.bduss = ''
        self.bdstoken = ''
        self.pcsett = ''
        self.session = requests.Session()
        self._load_cookies_from_file()
        self.cookies = self.session.cookies
        self.all_files = []

    def _load_cookies_from_file(self):
        """Load cookies file if file exist."""
        if os.access(global_config.cookies, os.F_OK):
            with open(global_config.cookies) as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
            self.session.cookies = cookies
            # NOT SURE stoken is bdstoken!
            self.token = self.session.cookies.get('STOKEN')
            self.baiduid = self.session.cookies.get('BAIDUID')
            self.bduss = self.session.cookies.get('BDUSS')
            return True
        return False

    def _save_img(self, img_url):
        """Download vcode image and save it to path of source code."""
        r = self.session.get(img_url)
        data = r.content
        img_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), VCODE)
        with open(img_path, mode='wb') as fp:
            fp.write(data)
        print("Saved verification code to ",
              os.path.dirname(os.path.abspath(__file__)))

    def _try_open_img(self, vcode):
        _platform = platform.system().lower()
        if _platform == 'darwin':
            os.system('open ' + vcode)
        elif _platform == 'windows':
            os.system('start ' + vcode)
        elif _platform == 'linux':
            os.system('xdg-open %s > /dev/null 2>&1 &' % vcode)

    def _handle_captcha(self, bdstoken=None):
        url = BAIDUPAN_SERVER + 'getcaptcha'
        d = {}
        extra_params = {
            'prod': 'share',
        }
        if bdstoken:
            extra_params['bdstoken'] = bdstoken
        res = self._request(base_url=url, extra_params=extra_params)
        if res.ok:
            t = res.json()
            self._save_img(t['vcode_img'])
            self._try_open_img(os.path.join(
                os.path.dirname(os.path.abspath(__file__)), VCODE))
            vcode_input = raw_input("Please input the captcha:\n")
            d['vcode_str'] = t['vcode_str']
            d['vcode_input'] = vcode_input
        return d

    @staticmethod
    def _dict_to_utf8(dictionary):
        """Convert dictionary's value to utf-8"""
        if not isinstance(dictionary, dict):
            return
        for k, v in dictionary.items():
            if isinstance(v, unicode):
                dictionary[k] = v.encode('utf-8')

    def bdlist(self, shareinfo, path, page=1):
        url = 'http://pan.baidu.com/share/list'
        payload = {
            'uk': shareinfo.uk,
            'shareid': shareinfo.share_id,
            'page': page,
            'num': 100,
            'dir': path,
            'order': 'time',
            'desc': 1,
            '_': int(time()*1000),
            'bdstoken': '',
            'channel': 'chunlei',
            'web': 1,
            'app_id': shareinfo.fileinfo[0]['app_id'],
            'clienttype': 0,
            'logid': ''
        }
        resp = self.session.get(url, params=payload, headers=self.headers)
        # FIXME catch parsing error
        data = json.loads(resp.text)
        if data['errno'] == 0:
            return data['list']
        else:
            # FIXME handle exception
            pass

    def _get_js(self, link, secret=None):
        """Get javascript code in html which contains share files info
        :param link: netdisk sharing link(publib or private).
        :type link: str
        :return str or None
        """
        if len(self.cookies) == 0:
            req = self.session.get(link, headers=self.headers)
        req = self.session.get(link, headers=self.headers)
        if 'init' in req.url:
            self.verify_passwd(req.url, secret)
            req = self.session.get(link)
        # util.save_cookies(self.session.cookies)
        data = req.text
        js_pattern = re.compile(
            '<script\stype="text/javascript">!function\(\)([^<]+)</script>', re.DOTALL)
        js = re.findall(js_pattern, data)
        return js[0] or None

    def get_file_info(self, shareinfo, fsid, secret=None):
        fi = FileInfo()

        extra_params = dict(bdstoken=shareinfo.bdstoken,
                            sign=shareinfo.sign, timestamp=shareinfo.timestamp)

        post_form = {
            'encrypt': '0',
            'product': 'share',
            'uk': shareinfo.uk,
            'primaryid': shareinfo.share_id,
            'fid_list': json.dumps([fsid]),
        }
        if self.session.cookies.get('BDCLND'):
            post_form['extra'] = '{"sekey":"%s"}' % (
                url_unquote(self.session.cookies['BDCLND'])),
        logger.debug(post_form, extra={'type': 'form', 'method': 'POST'})

        url = BAIDUPAN_SERVER + 'sharedownload'
        while True:
            response = self._request(
                'POST', url, extra_params=extra_params, post_data=post_form)
            if not response.ok:
                raise UnknownError
            _json = response.json()
            errno = _json['errno']
            logger.debug(_json, extra={'type': 'json', 'method': 'POST'})

            if errno == 0:
                fi.filename = _json['list'][0]['server_filename']
                fi.path = os.path.dirname(_json['list'][0]['path'])
                fi.dlink = _json['list'][0]['dlink']
                fi.parent_path = url_unquote(shareinfo.fileinfo[0]['parent_path'].encode('utf8'))
                break
            elif errno == -20:
                verify_params = self._handle_captcha(shareinfo.bdstoken)
                post_form.update(verify_params)
                response = self._request(
                    'POST', url, extra_params=extra_params, post_data=post_form)
                _json = response.json()
                errno = _json['errno']
                continue
            elif errno == 116:
                raise DownloadError("The share file does not exist")
            else:
                raise UnknownError
        return fi

    def get_file_infos(self, link, secret=None):
        shareinfo = ShareInfo()
        js = None
        try:
            js = self._get_js(link, secret)
        except IndexError:
            # Retry with new cookies
            js = self._get_js(link, secret)

        # Fix #15
        self.session.get(
            'http://d.pcs.baidu.com/rest/2.0/pcs/file?method=plantcookie&type=ett')
        self.pcsett = self.session.cookies.get('pcsett')
        logger.debug(self.pcsett, extra={
                     'type': 'cookies', 'method': 'SetCookies'})

        if not shareinfo.match(js):
            pass

        for fi in shareinfo.fileinfo:
            if fi['isdir'] == 0:
                self.all_files.append(fi)
            else:
                # recursively get files under the specific path
                self.bd_get_files(shareinfo, fi['path'])

        # get file details include dlink, path, filename ...
        return [self.get_file_info(shareinfo, fsid=f['fs_id'], secret=secret) for f in self.all_files]

    def bd_get_files(self, shareinfo, path):
        # Let's do a maximum of 100 pages
        file_list = []
        for page in range(1, 100):
            print('Fetching page', page)
            file_list_new = self.bdlist(shareinfo, path, page)
            file_list.extend(file_list_new)
            if len(file_list_new) != 100:
                break
        for f in file_list:
            if f['isdir'] == 0:
                self.all_files.append(f)
            else:
                self.bd_get_files(shareinfo, f['path'])

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
            pwd = input("Please input this sharing password\n")
        data = {'pwd': pwd, 'vcode': '', 'vcode_str': ''}
        verify_url = "{0}&t={1}&channel=chunlei&clienttype=0&web=1".format(url.replace('init', 'verify'), int(time()))
        logger.debug(url, extra={'type': 'url', 'method': 'POST'})
        headers = self.headers.copy()
        headers['Referer'] = url
        r = self.session.post(url=verify_url, data=data, headers=headers)
        mesg = r.json()
        logger.debug(mesg, extra={'type': 'JSON', 'method': 'POST'})
        errno = mesg.get('errno')
        if errno == -63:
            raise UnknownError
        elif errno == -9:
            raise VerificationError("提取密码错误\n")

    def _request(self, method='GET', base_url='', extra_params=None, post_data=None, **kwargs):
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
            'bdstoken': self.bdstoken,
        }
        if isinstance(extra_params, dict):
            params.update(extra_params)
            self._dict_to_utf8(params)
        if method == 'GET' and base_url:
            response = self.session.get(
                base_url, params=params, headers=self.headers, **kwargs)
        elif method == 'POST' and base_url and post_data:
            response = self.session.post(
                base_url, data=post_data, params=params, headers=self.headers, **kwargs)
        else:
            response = None
        return response

class FileInfo(object):
    def __init__(self):
        self.filename = None
        self.path = None
        self.dlink = None

class ShareInfo(object):
    pattern = re.compile('yunData\.setData\((.*?)\);')
    filename_pattern = re.compile('"server_filename":"([^"]+)"', re.DOTALL)
    fileinfo_pattern = re.compile('yunData\.FILEINFO\s=\s(.*);')

    def __init__(self):
        self.share_id = None
        self.bdstoken = None
        self.uk = None
        self.bduss = None
        self.sign = None
        self.timestamp = None
        self.sharepagetype = None
        self.fileinfo = None

    def __call__(self, js):
        return self.match(js)

    def __repr__(self):
        return '<ShareInfo %r>' % self.share_id

    def match(self, js):
        _filename = re.search(self.filename_pattern, js)
        if _filename:
            self.filename = _filename.group(1).decode('unicode_escape')

        data = re.findall(self.pattern, js)[0]
        if not data:
            return False
        yun_data = json.loads(data)
        self.fileinfo = yun_data["file_list"]["list"]

        logger.debug(yun_data, extra={'method': 'GET', 'type': 'javascript'})
        # if 'single' not in yun_data.get('SHAREPAGETYPE') or '0' in yun_data.get('LOGINSTATUS'):
        #    return False
        self.uk = yun_data.get('uk')
        # self.bduss = yun_data.get('MYBDUSS').strip('"')
        self.share_id = yun_data.get('shareid')
        self.sign = yun_data.get('sign')
        if yun_data.get('bdstoken'):
            self.bdstoken = yun_data.get('bdstoken')
        self.timestamp = yun_data.get('timestamp')
        # if self.bdstoken:
        #    return True
        return True


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
