#!/usr/bin/env python2
#!coding=utf-8

from time import time
import json
import logging
import re
import os
from urllib import urlencode
import urllib2
import cookielib

from config import configure

# logging.basicConfig(level=logging.DEBUG)


class BaiduAccount(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36',
    }

    def __init__(self, username, passwd, cookie_filename):
        self.username = username
        self.passwd = passwd
        self.cookie_filename = cookie_filename
        self.cj = cookielib.LWPCookieJar(cookie_filename)
        self.opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(),
            urllib2.HTTPCookieProcessor(self.cj)
        )
        self.codestring = ''
        self.time = int(time())
        self._check_url = 'https://passport.baidu.com/v2/api/?logincheck&callback=bdPass.api.login._needCodestring' \
                          'CheckCallback&tpl=mn&charset=utf-8&index=0&username=%s&time=%d'
        self._token_url = 'https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true'
        self._post_url = 'https://passport.baidu.com/v2/api/?login'
        # debug:
        # self._post_url = 'http://httpbin.org/post'
        self.token = ''
        self.baiduid = ''
        self.bduss = ''

    def _get_badidu_uid(self):
        self.opener.open('http://www.baidu.com')
        for cookie in self.cj:
            if cookie.name == 'BAIDUID':
                self.baiduid = cookie.value
        logging.debug(self.baiduid)

    def _check_verify_code(self):
        r = self.opener.open(self._check_url % (self.username, self.time))
        s = r.read()
        data = json.loads(s[s.index('{'):-1])
        logging.debug(data)
        # TODO
        # 验证码
        if data.get('errno'):
            self.codestring = data.get('codestring')

    def _get_token(self):
        r = self.opener.open(self._token_url)
        s = r.read()
        try:
            self.token = re.search("login_token='(\w+)';", s).group(1)
            logging.debug(self.token)
        except:
            raise GetTokenError("Can't get the token")

    def _post_data(self):
        post_data = {'ppui_logintime': '9379', 'charset': 'utf-8', 'codestring': '', 'token': self.token,
                     'isPhone': 'false', 'index': '0', 'u': '', 'safeflg': 0,
                     'staticpage': 'http://www.baidu.com/cache/user/html/jump.html', 'loginType': '1', 'tpl': 'mn',
                     'callback': 'parent.bdPass.api.login._postCallback', 'username': self.username,
                     'password': self.passwd, 'verifycode': '', 'mem_pass': 'on'}
        post_data = urlencode(post_data)
        logging.debug(post_data)
        self.opener.open(self._post_url, data=post_data)
        for cookie in self.cj:
            if cookie.name == 'BDUSS':
                self.bduss = cookie.value
        logging.debug(self.bduss)
        self.cj.save()

    def login(self):
        self._get_badidu_uid()
        self._check_verify_code()
        if self.codestring:
            # TODO
            # 验证码处理
            pass
        self._get_token()
        self._post_data()
        logging.debug(self.cj)
        if not self.bduss and not self.baiduid:
            raise LoginError('登陆异常')

    def load_cookies_from_file(self):
        # if cookie exist
        if os.access(self.cookie_filename, os.F_OK):
            self.cj.load()
            for cookie in self.cj:
                if cookie.name == 'BAIDUID':
                    self.baiduid = cookie.value
                elif cookie.name == 'BDUSS':
                    self.bduss = cookie.value


class GetTokenError(Exception):
    pass


class LoginError(Exception):
    pass


def login(args):
    if args:
        username = args[0]
        passwd = args[1]
    else:
        username = configure.username
        passwd = configure.password
    if not username and not passwd:
        raise LoginError('请输入你的帐号密码！')
    cookies = configure.cookies
    account = BaiduAccount(username, passwd, cookies)
    account.login()
    print "Saving session to %s" % cookies