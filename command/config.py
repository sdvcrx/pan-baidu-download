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
    def cookies(self):
        cookies = self.configfile.get('option', 'cookies')
        return os.path.expanduser(cookies)

    @cookies.setter
    def cookies(self, cookies_path):
        self.configfile.set('option', 'cookies', cookies_path)
        with open(name=self.path, mode='w') as fp:
            self.configfile.write(fp)

configure = Config()


def config(configuration):
    if len(configuration) == 0:
        print 'limit = %s' % configure.limit
        print 'dir = %s' % configure.dir
        print 'cookies = %s' % configure.cookies
    elif configuration[0] == 'limit':
        configure.limit = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'dir':
        configure.dir = configuration[1]
        print 'Saving configuration to config.ini'
    elif configuration[0] == 'cookies':
        configure.cookies = configuration[1]
        print 'Saving configuration to config.ini'
    else:
        raise TypeError('修改配置错误')
    sys.exit(0)
