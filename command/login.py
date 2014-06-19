#!/usr/bin/env python2
# coding=utf-8

from time import time
import json
import re
import os
from urllib import urlencode
import urllib2
import cookielib

from util import logger
from config import global_config

__all__ = ['login']


class BaiduAccount(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36',
    }

    def __init__(self, username, passwd, cookie_filename):
        """
        Login and save cookies to file.

        :type username: str
        :type passwd: str
        :type cookie_filename: str
        :param username: Baidu username.
        :param passwd: Baidu account password.
        :param cookie_filename: cookies file name.
        :return: None
        """
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
        self._time = int(time())
        self._check_url = 'https://passport.baidu.com/v2/api/?logincheck&callback=bdPass.api.login._needCodestring' \
                          'CheckCallback&tpl=mn&charset=utf-8&index=0' \
                          '&username={self.username}&time={self._time}'.format(self=self)
        self._token_url = 'https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true'
        self._post_url = 'https://passport.baidu.com/v2/api/?login'
        # debug:
        # self._post_url = 'http://httpbin.org/post'
        self.token = ''
        self.baiduid = ''
        self.bduss = ''

    def _get_baidu_uid(self):
        """Get BAIDUID."""
        self.opener.open('http://www.baidu.com')
        for cookie in self.cj:
            if cookie.name == 'BAIDUID':
                self.baiduid = cookie.value
        log_message = {'type': 'baidu uid', 'method': 'GET'}
        logger.debug(self.baiduid, extra=log_message)

    def _check_verify_code(self):
        """Check if login need to input verify code."""
        r = self.opener.open(self._check_url)
        s = r.read()
        data = json.loads(s[s.index('{'):-1])
        log_message = {'type': 'check loging verify code', 'method': 'GET'}
        logger.debug(data, extra=log_message)
        # TODO: 验证码
        if data.get('errno'):
            self.codestring = data.get('codestring')

    def _get_token(self):
        """Get bdstoken."""
        r = self.opener.open(self._token_url)
        s = r.read()
        try:
            self.token = re.search("login_token='(\w+)';", s).group(1)
            log_message = {'type': 'bdstoken', 'method': 'GET'}
            logger.debug(self.token, extra=log_message)
        except:
            raise GetTokenError("Can't get the token")

    def _post_data(self):
        """Post login form."""
        post_data = {'ppui_logintime': '9379', 'charset': 'utf-8', 'codestring': '', 'token': self.token,
                     'isPhone': 'false', 'index': '0', 'u': '', 'safeflg': 0,
                     'staticpage': 'http://www.baidu.com/cache/user/html/jump.html', 'loginType': '1', 'tpl': 'mn',
                     'callback': 'parent.bdPass.api.login._postCallback', 'username': self.username,
                     'password': self.passwd, 'verifycode': '', 'mem_pass': 'on'}
        post_data = urlencode(post_data)
        log_message = {'type': 'login post data', 'method': 'POST'}
        logger.debug(post_data, extra=log_message)
        self.opener.open(self._post_url, data=post_data)
        for cookie in self.cj:
            if cookie.name == 'BDUSS':
                self.bduss = cookie.value
        log_message = {'type': 'BDUSS', 'method': 'GET'}
        logger.debug(self.bduss, extra=log_message)
        self.cj.save()

    def login(self):
        self._get_baidu_uid()
        self._check_verify_code()
        if self.codestring:
            # TODO: 验证码处理
            pass
        self._get_token()
        self._post_data()
        if not self.bduss and not self.baiduid:
            raise LoginError('登陆异常')

    def load_cookies_from_file(self):
        """Load cookies file if file exist."""
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
    """
    Login.

    :type args: list or tuple
    :param args: username and password or emtyp.
    :raise LoninError: if username or passwd is empty.
    :return: None
    """
    if args:
        username = args[0]
        passwd = args[1]
    else:
        username = global_config.username
        passwd = global_config.password
    if not username and not passwd:
        raise LoginError('请输入你的帐号密码！')
    cookies = global_config.cookies
    account = BaiduAccount(username, passwd, cookies)
    account.login()
    print("Saving session to {}".format(cookies))
