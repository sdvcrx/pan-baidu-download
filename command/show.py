from __future__ import print_function

import sys

from bddown_core import Pan
from util import bd_help


def show(links):
    if not len(links):
        bd_help('show')
    else:
        for url in links:
            pan = Pan()
            info = pan.get_dlink(url)
            print(u"{0}\n{1}\n\n".format(info.filename, info.dlink).encode('utf-8'))
    sys.exit(0)
