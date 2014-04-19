#!/usr/bin/env python

import sys
import logging
import argparse
import subprocess

from bddown_core import Pan, Album
from util import convert_none, parse_url, add_http
from config import global_config


def download_command(filename, link, limit=None, output_dir=None):
    bool(output_dir) and not os.path.exists(output_dir) and os.makedirs(output_dir)
    print "\033[32m" + filename + "\033[0m"
    firefox_ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'
    cmd = "aria2c -c -o '%(filename)s' -s5 -x5" \
          " --user-agent='%(useragent)s' --header 'Referer:http://pan.baidu.com/disk/home'" \
          " %(limit)s %(dir)s '%(link)s'" % {
              "filename": filename,
              "useragent": firefox_ua,
              "limit": convert_none('--max-download-limit=', limit),
              "dir": convert_none('--dir=', output_dir),
              "link": link
          }
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
    links = map(add_http, links)        # add 'http://'
    for url in links:
        res = parse_url(url)
        # normal
        if res.get('type') == 1:
            pan = Pan(url, secret=secret)
            count = 1
            while count != 0:
                link, filename, count = pan.info
                download_command(filename, link, limit=limit, output_dir=output_dir)

        # album
        elif res.get('type') == 2:
            album_id = res.get('album_id')
            uk = res.get('uk')
            album = Album(album_id, uk)
            count = 1
            while count != 0:
                link, filename, count = album.info
                download_command(filename, link, limit=limit, output_dir=output_dir)
        # home
        elif res.get('type') == 3:
            raise NotImplementedError('This function has not implemented.')
        elif res.get('type') == 0:
            logging.debug(url)
            continue
        else:
            continue

    sys.exit(0)
