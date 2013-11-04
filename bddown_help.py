#!/usr/bin/env python2
#!coding=utf-8

basic_command = [
    ('help',        'Show this help'),
    ('download',    'Download file from the Baidu pan link'),
    ('show',        'Show the Baidu pan real link and filename'),
    ('config',      'save configuration to file')
]

extended_usage = ''


def join_commands(command):
    n = max(len(x[0]) for x in command)
    n = max(n, 10)
    return ''.join(' %%-%ds %%s\n' % n % (h, k) for (h, k) in basic_command)

basic_usage = '''python bddown_cli.py <command> [<args>]

Basic commands:
''' + join_commands(basic_command)


def usage():
    return basic_usage + '''
Use python bddown_cli.py help for details
Use python bddown_cli.py help <command> for more information on a specific command.
Check https://github.com/banbanchs/pan-baidu-download for details'''


def show_help():
    return ''' Python script for Baidu pan
Basic usage:
    ''' + basic_usage + extended_usage + '\n'


download = '''python bddown_cli.py download [options] [Baidupan-url]...

Download file from the Baidu pan link

Options:
    --limit=[speed]             Max download speed limit.
    --output-dir=[dir]          Download task to dir.'''

show = '''python bddown_cli.py show [Baidupan-url]...

Show the real download link and filename

Example:
python bddown_cli.py show http://pan.baidu.com/s/15lliC
'''

config = '''python bddown_cli.py config [command]...

save configuration to file

Options:
    --limit=[speed]             Max download speed limit.
    --output-dir=[dir]          Download task to dir.'''

help_help = '''Get helps:
 python lixian_cli.py help help
 python lixian_cli.py help examples
 python lixian_cli.py help readme
 python lixian_cli.py help <command>'''

help = help_help