#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse
import subprocess

from bddown_core import Pan
from util import convert_none, parse_url, add_http, logger
from config import global_config


def download_command(filename, link, cookies, limit=None, output_dir=None):
    reload(sys)
    sys.setdefaultencoding("utf-8")
    bool(output_dir) and not os.path.exists(output_dir) and os.makedirs(output_dir)
    print("\033[32m" + filename + "\033[0m")
    pan_ua = 'netdisk;4.4.0.6;PC;PC-Windows;6.2.9200;WindowsBaiduYunGuanJia'
    cmd = 'aria2c -c -o "{filename}" -s5 -x5' \
          ' --user-agent="{useragent}" --header "Referer:http://pan.baidu.com/disk/home"' \
          ' {cookies} {limit} {dir}' \
          ' "{link}"'.format(filename=filename, useragent=pan_ua, link=link,
                             cookies=convert_none("--header \"Cookies: ", cookies),
                             limit=convert_none('--max-download-limit=', limit),
                             dir=convert_none('--dir=', output_dir))
    subprocess.call(cmd, shell=True)


def download(args):
    limit = global_config.limit
    output_dir = global_config.dir
    parser = argparse.ArgumentParser(description="download command arg parser")
    parser.add_argument('-L', '--limit', action="store", dest='limit', help="Max download speed limit.")
    parser.add_argument('-D', '--dir', action="store", dest='output_dir', help="Download task to dir.")
    parser.add_argument('-S', '--secret', action="store", dest='secret', help="Retrieval password.", default="")
    if not args:
        parser.print_help()
        exit(1)
    namespace, links = parser.parse_known_args(args)
    secret = namespace.secret
    if namespace.limit:
        limit = namespace.limit
    if namespace.output_dir:
        output_dir = namespace.output_dir

    # if is wap
    links = [link.replace("wap/link", "share/link") for link in links]
    # add 'http://'
    links = map(add_http, links)
    for url in links:
        res = parse_url(url)
        # normal
        if res.get('type') == 1:
            pan = Pan()
            info = pan.get_dlink(url, secret)
            cookies = 'BDUSS={0}'.format(pan.bduss) if pan.bduss else ''
            if cookies and pan.pcsett:
                cookies += ';pcsett={0}'.format(pan.pcsett)
            if cookies:
                cookies += '"'
            download_command(info.filename, info.dlink, cookies=cookies, limit=limit, output_dir=output_dir)

        # album
        elif res.get('type') == 2:
            raise NotImplementedError('This function has not implemented.')
        # home
        elif res.get('type') == 3:
            raise NotImplementedError('This function has not implemented.')
        elif res.get('type') == 0:
            logger.debug(url, extra={"type": "wrong link", "method": "None"})
            continue
        else:
            continue

    sys.exit(0)
