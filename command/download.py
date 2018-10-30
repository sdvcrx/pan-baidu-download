#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import argparse
import subprocess

from bddown_core import Pan
from util import convert_none, parse_url, add_http, logger
from config import global_config


def download_command(filename, savedir, link, cookies, limit=None, output_dir=None):
    reload(sys)
    sys.setdefaultencoding("utf-8")
    bool(output_dir) and not os.path.exists(output_dir) and os.makedirs(output_dir)
    print("\033[32m" + filename + "\033[0m")
    pan_ua = 'netdisk;5.2.6;PC;PC-Windows;6.2.9200;WindowsBaiduYunGuanJia'
    cmd = 'aria2c -c -d "{savedir}" -o "{filename}" -s10 -x10' \
          ' --user-agent="{useragent}" --header "Referer:http://pan.baidu.com/disk/home"' \
          ' {cookies} {limit} {dir}' \
          ' "{link}"'.format(savedir=savedir, filename=filename, useragent=pan_ua, link=link,
                             cookies=convert_none("--header \"Cookie: ", cookies),
                             limit=convert_none('--max-download-limit=', limit),
                             dir=convert_none('--dir=', output_dir))
    print(cmd)
    subprocess.call(cmd, shell=True)

def select_download(fis):
    if len(fis) <= 1:
        return fis

    print("File list:")
    counter = 1
    for fi in fis:
        savedir = fi.path.replace(fi.parent_path, '', 1)[1:]
        print(str(counter) + ')', savedir + "/" + unicode(fi.filename).encode('utf8'))
        counter += 1

    input_numbers = raw_input("Please select files to download(e.g., 1,3-5,7):\n")
    selected_numbers = []
    for part in input_numbers.split(','):
        x = part.split('-')
        if len(x) == 1:
            selected_numbers += [int(x[0])]
        elif len(x) == 2:
            selected_numbers += range(int(x[0]), int(x[1])+1)
        else:
            print("Error, your input seems illegal." + str(len(x)))
            return None

    # ensure no duplicate numbers
    selected_numbers = list(set(selected_numbers))

    selected_fis = [fis[i-1] for i in selected_numbers]

    print("Download list:")
    counter = 1
    for sfi in selected_fis:
        savedir = sfi.path.replace(sfi.parent_path, '', 1)[1:]
        print(str(counter) + ')', savedir + "/" + unicode(sfi.filename).encode('utf8'))
        counter += 1

    return selected_fis

def matchExtension(filename, extension):
    _, file_ext = os.path.splitext(filename)
    return file_ext.lower()[1:] == extension.lower()

def download(args):
    limit = global_config.limit
    output_dir = global_config.dir
    parser = argparse.ArgumentParser(description="download command arg parser")
    parser.add_argument('-L', '--limit', action="store", dest='limit', help="Max download speed limit.")
    parser.add_argument('-D', '--dir', action="store", dest='output_dir', help="Download task to dir.")
    parser.add_argument('-S', '--secret', action="store", dest='secret', help="Retrieval password.", default="")
    parser.add_argument('-P', '--partial', action="count", help="Partial download.")
    parser.add_argument('-E', '--extension', action="store", dest='extension', help="Download only specified by the extension. e.g. aw3")

    if not args:
        parser.print_help()
        exit(1)
    namespace, links = parser.parse_known_args(args)
    secret = namespace.secret
    if namespace.limit:
        limit = namespace.limit
    if namespace.output_dir:
        output_dir = namespace.output_dir

    extension = namespace.extension

    # if is wap
    links = [link.replace("wap/link", "share/link") for link in links]
    # add 'http://'
    links = map(add_http, links)
    for url in links:
        res = parse_url(url)
        # normal
        if res.get('type') == 1:
            pan = Pan()
            fis = pan.get_file_infos(url, secret)

            if namespace.partial:
                while True:
                    fis = select_download(fis)
                    if fis is not None:
                        break

            for fi in fis:
                if extension and not matchExtension(fi.filename, extension):
                    print('{filename} is igonred'.format(filename=fi.filename))
                    continue
                cookies = 'BDUSS={0}'.format(pan.bduss) if pan.bduss else ''
                if cookies and pan.pcsett:
                    cookies += ';pcsett={0}'.format(pan.pcsett)
                if cookies:
                    cookies += '"'

                savedir = fi.path.replace(fi.parent_path, '', 1)[1:]
                download_command(fi.filename, savedir, fi.dlink, cookies=cookies, limit=limit, output_dir=output_dir)

        elif res.get('type') == 4:
            pan = Pan()
            fsid = res.get('fsid')
            newUrl = res.get('url')
            infos = pan.get_file_infos(newUrl, secret, fsid)
            cookies = 'BDUSS={0}'.format(pan.bduss) if pan.bduss else ''
            if cookies and pan.pcsett:
                cookies += ';pcsett={0}'.format(pan.pcsett)
            if cookies:
                cookies += '"'
            for info in infos:
                if extension and not matchExtension(info.filename, extension):
                    print('{filename} is ignored'.format(filename=info.filename))
                    continue
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
