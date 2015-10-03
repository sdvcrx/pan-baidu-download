#!/usr/bin/env python2
# coding=utf-8

from time import time
import json
import re
import os
import pickle

from requests import Session
import requests.utils

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
        self.session = Session()
        self.codestring = ''
        self._time = int(time())
        self._check_url = 'https://passport.baidu.com/v2/api/?logincheck&callback=bdPass.api.login._needCodestring' \
                          'CheckCallback&tpl=mn&charset=utf-8&index=0' \
                          '&username={self.username}&time={self._time}'.format(self=self)
        self._token_url = 'https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true'
        self._post_url = 'https://passport.baidu.com/v2/api/?login'
        self._genimage_url = 'https://passport.baidu.com/cgi-bin/genimage?{code}'
        # debug:
        # self._post_url = 'http://httpbin.org/post'
        self.token = ''
        self.baiduid = ''
        self.bduss = ''

    def _get_baidu_uid(self):
        """Get BAIDUID."""
        self.session.get('http://www.baidu.com')
        self.baiduid = self.session.cookies.get('BAIDUID')
        log_message = {'type': 'baidu uid', 'method': 'GET'}
        logger.debug(self.baiduid, extra=log_message)

    def _check_verify_code(self):
        """Check if login need to input verify code."""
        r = self.session.get(self._check_url)
        s = r.text
        data = json.loads(s[s.index('{'):-1])
        log_message = {'type': 'check loging verify code', 'method': 'GET'}
        logger.debug(data, extra=log_message)
        if data.get('codestring'):
            self.codestring = data.get('codestring')

    def _handle_verify_code(self):
        """Save verify code to filesystem and prompt user to input."""
        r = self.session.get(self._genimage_url.format(code=self.codestring))
        # TODO: Handle different verify code image format: jpg or gif
        img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'vcode.jpg')
        with open(img_path, mode='wb') as fp:
            fp.write(r.content)
        print("Saved verification code to {}".format(os.path.dirname(img_path)))
        vcode = raw_input("Please input the captcha:\n")
        return vcode

    def _get_token(self):
        """Get bdstoken."""
        r = self.session.get(self._token_url)
        s = r.text
        try:
            self.token = re.search("login_token='(\w+)';", s).group(1)
            # FIXME: if couldn't get the token, we can not get the log message.
            log_message = {'type': 'bdstoken', 'method': 'GET'}
            logger.debug(self.token, extra=log_message)
        except:
            raise GetTokenError("Can't get the token")

    def _post_data(self, code):
        """Post login form."""
        post_data = {'ppui_logintime': '9379', 'charset': 'utf-8', 'codestring': self.codestring, 'token': self.token,
                     'isPhone': 'false', 'index': '0', 'u': '', 'safeflg': 0,
                     'staticpage': 'http://www.baidu.com/cache/user/html/jump.html', 'loginType': '1', 'tpl': 'mn',
                     'callback': 'parent.bdPass.api.login._postCallback', 'username': self.username,
                     'password': self.passwd, 'verifycode': code, 'mem_pass': 'on'}
        # post_data = urlencode(post_data)
        log_message = {'type': 'login post data', 'method': 'POST'}
        logger.debug(post_data, extra=log_message)
        response = self.session.post(self._post_url, data=post_data)
        s = response.text
        log_message = {'type': 'response', 'method': 'POST'}
        logger.debug(s, extra=log_message)
        self.bduss = response.cookies.get("BDUSS")
        log_message = {'type': 'BDUSS', 'method': 'GET'}
        logger.debug(self.bduss, extra=log_message)
        return s

    def _save_cookies(self):
        with open(self.cookie_filename, 'w') as f:
            pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

    def login(self):
        code = ''
        self._get_baidu_uid()
        self._check_verify_code()
        if self.codestring:
            code = self._handle_verify_code()
        self._get_token()
        self._post_data(code)
        if not self.bduss or not self.baiduid:
            raise LoginError('登陆异常')
        self._save_cookies()

    def load_cookies_from_file(self):
        """Load cookies file if file exist."""
        if os.access(self.cookie_filename, os.F_OK):
            with open(self.cookie_filename) as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
            self.session.cookies = cookies
            # NOT SURE stoken is bdstoken!
            # self.token = self.session.cookies.get('STOKEN')
            self.baiduid = self.session.cookies.get('BAIDUID')
            self.bduss = self.session.cookies.get('BDUSS')


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
