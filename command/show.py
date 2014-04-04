import sys

from bddown_core import Pan
from util import bd_help


def show(links):
    if not len(links):
        bd_help('show')
    else:
        for url in links:
            pan = Pan(url)
            count = 1
            while count != 0:
                link, filename, count = pan.info
                print "%s\n%s\n\n" % (filename, link)
    sys.exit(0)