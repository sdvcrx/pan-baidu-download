import sys

from bddown_core import BaiduDown
from util import bd_help


def show(links):
    if not len(links):
        bd_help('show')
    else:
        for url in links:
            pan = BaiduDown(url)
            filename = pan.filename
            link = pan.link
            print "%s\n%s\n\n" % (filename, link)
    sys.exit(0)