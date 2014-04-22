#!/usr/bin/env python2
# coding=utf-8

import os
import sys
import ConfigParser

command = ('limit', 'dir', 'cookies', 'username', 'password', 'jsonrpc')


class Config(object):
    def __init__(self):
        # get config.ini path
        self._path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), 'config.ini')
        if not os.path.exists(self._path):
            raise IOError("No such file: config.ini")
        self._configfile = ConfigParser.ConfigParser(allow_no_value=True)
        self._configfile.read(self._path)
        self.config = dict(self._configfile.items('option'))

    def __getattr__(self, item):
        # expand '~/Downloads' to '/home/XXX/Downloads'
        if item in ('dir', 'cookies'):
            return os.path.expanduser(self.config.get(item))
        return self.config.get(item)

    def get(self, k, v=None):
        return self.config.get(k, v)

    def put(self, k, v):
        # if k in ('dir', 'cookies'):
        #     v = os.path.expanduser(v)
        self.config[k] = v
        self._save_config(k, v)

    def delete(self, k):
        if k in self.config.iterkeys():
            self.config[k] = ""
            self._save_config(k)

    def _save_config(self, k, v=""):
        self._configfile.set('option', k, v)
        with open(name=self._path, mode='w') as fp:
            self._configfile.write(fp)

global_config = Config()


def config(configuration):
    if len(configuration) == 0:
        for k, v in global_config.config.iteritems():
            print '{0} -> {1}'.format(k, v)
    elif configuration[0] == 'delete':
        global_config.delete(configuration[1])
        print 'Successfully delete {}'.format(configuration[1])
    elif configuration[0] in command:
        try:
            global_config.put(configuration[0], configuration[1])
        except IndexError:
            # avoid like this case
            # $ pan config limit
            raise IndexError('Please input value of {}!'.format(configuration[0]))
        print 'Saving configuration to config.ini'
    else:
        raise TypeError('修改配置错误')
    sys.exit(0)
