#!/usr/bin/env python2
#!coding=utf-8
import sys
import os
import re
import urllib2
import json
import pdb

def getDownloadPage(url):
    header = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64)\
                        AppleWebKit/537.36 (KHTML, like Gecko)\
                        Chrome/28.0.1500.95 Safari/537.36'
    }
    request = urllib2.Request(url = url, headers = header)
    data = urllib2.urlopen(request).read()
    script_pattern = re.compile(r'<script type="text/javascript">(.+?)</script>', re.DOTALL)
    script = re.findall(script_pattern, data)[2]
    pdb.set_trace()
    return script

def getFileName(data):
    pattern = re.compile(r'var\sserver_filename="(.+?)"')
    filename = re.search(pattern, data).group(1)
    pdb.set_trace()
    return filename

def getDownloadLink(data):
    pattern = re.compile(r'dlink\\.+?(http.+?)\\"')
    link = re.search(pattern, data).group(1).replace('\\', '')
    return link

def download(link, filename):
    cmd = "aria2c -c -o '%s' -s5 -x5 '%s'" % (filename, link)
    os.system(cmd)


def main(urls):
    for url in urls:
        script = getDownloadPage(url)
        filename = getFileName(script)
        link = getDownloadLink(script)
        download(link, filename)
        print "%s complete" % filename
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "No action specified."
        sys.exit()
    if sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if option == 'version':
            print 'V0.2'
        elif option == 'help':
            print '''\
                Default aria2c -c -s5 -x5
              --version: Print the version
              --help   : Display this help'''
        else:
            print 'Unknow option'
        sys.exit()
    else:
        main(sys.argv[1:])

