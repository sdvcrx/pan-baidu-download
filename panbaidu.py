#!/usr/bin/env python2
#!coding=utf-8
import sys
import os
import re
import urllib2

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
    return script

def getFileName(data):
    pattern = re.compile(r'var\sserver_filename="(.+?)"')
    filename = re.search(pattern, data).group(1)
    return filename

def getDownloadLink(data):
    pattern = re.compile(r'\\"dlink\\":\\"(.*?&sh=1)')
    link = re.search(pattern, data).group(1).replace('\\', '')
    return link

def download(link, filename, limit=None):
    if limit:
        cmd = "aria2c -c -o '%s' -s5 -x5 %s '%s'" % (filename, limit, link)
    else:
        cmd = "aria2c -c -o '%s' -s5 -x5 '%s'" % (filename, link)
    os.system(cmd)


def main(urls, limit=None):
    for url in urls:
        script = getDownloadPage(url)
        filename = getFileName(script)
        link = getDownloadLink(script)
        download(link, filename, limit)
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "No action specified."
        sys.exit()
    if sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if option == 'version':
            print 'V0.4'
        elif option == 'help':
            print '''\
                Default aria2c -c -s5 -x5
              --version: Print the version
              --help   : Display this help
              --max-download-limit=XXk|XXm: Limit max download speed to XX kb or XX mb'''
        elif re.match(r'--max-download-limit=\d+k', sys.argv[1]):
            main(sys.argv[2:], sys.argv[1])
        else:
            print 'Unknow option'
        sys.exit()
    else:
        main(sys.argv[1:])

