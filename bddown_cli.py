#!/usr/bin/env python2
#!coding=utf-8

import sys

#from bddown_help import *
import bddown_help
from util import *
from bddown_core import generate_download_queue, show, config


def execute_command(args=sys.argv[1:]):
    if not args:
        print usage()
        sys.exit(1)

    command = args[0]
    if command.startswith('-'):
        if command in ('-h', '--help'):
            usage(bddown_help.show_help())
        elif command in ('-V', '-v', '--version'):
            print 'V1.54'
        else:
            usage()
            sys.exit(1)
        sys.exit(0)

    commands = {
        'help':         bd_help,
        'download':     generate_download_queue,
        'show':         show,
        'config':       config
    }

    if command not in commands.keys():
        usage()
        sys.exit(1)
    elif '-h' in args or '--help' in args:
        bd_help([command])
        sys.exit(0)
    else:
        commands[command](args[1:])


if __name__ == '__main__':
    execute_command()
