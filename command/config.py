#!/usr/bin/env python2
#!coding=utf-8

import os
import sys
import ConfigParser


class Config(object):
    def __init__(self):
        # get config.ini path
        self.path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), 'config.ini')
        self.configfile = ConfigParser.ConfigParser(allow_no_value=True)
        self.configfile.read(self.path)

    @property
    def limit(self):
        return self.configfile.get('option', 'limit')

    @limit.setter
    def limit(self, new_limit):
        self.configfile.set('option', 'limit', new_limit)
        self.save_config()

    @property
    def dir(self):
        path = self.configfile.get('option', 'dir')
        return os.path.expanduser(path)

    @dir.setter
    def dir(self, new_dir):
        self.configfile.set('option', 'dir', new_dir)
        self.save_config()

    @property
    def cookies(self):
        cookies = self.configfile.get('option', 'cookies')
        return os.path.expanduser(cookies)

    @cookies.setter
    def cookies(self, cookies_path):
        self.configfile.set('option', 'cookies', cookies_path)
        self.save_config()

    @property
    def username(self):
        return self.configfile.get('option', 'username')

    @username.setter
    def username(self, new_name):
        self.configfile.set('option', 'username', new_name)
        self.save_config()

    @property
    def password(self):
        return self.configfile.get('option', 'password')

    @password.setter
    def password(self, new_passwd):
        self.configfile.set('option', 'password', new_passwd)
        self.save_config()

    @property
    def jsonrpc(self):
        return self.configfile.get('option', 'jsonrpc')

    @jsonrpc.setter
    def jsonrpc(self, new_path):
        self.configfile.set('option', 'jsonrpc', new_path)
        self.save_config()

    def save_config(self):
        with open(name=self.path, mode='w') as fp:
            self.configfile.write(fp)

configure = Config()


def config(configuration):
    if len(configuration) == 0:
        print 'limit = %s' % configure.limit
        print 'dir = %s' % configure.dir
        print 'cookies = %s' % configure.cookies
        print 'username = %s' % configure.username
        print 'password = %s' % configure.password
        print 'jsonprc  = %s' % configure.jsonrpc
    elif configuration[0] == 'limit':
        configure.limit = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'dir':
        configure.dir = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'cookies':
        configure.cookies = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'username':
        configure.username = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'password':
        configure.password = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'jsonrpc':
        configure.jsonrpc = configuration[1]
    else:
        raise TypeError('修改配置错误')
    sys.exit(0)
