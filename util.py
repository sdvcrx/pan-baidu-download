import bddown_help


def bd_help(args):
    if len(args) == 1:
        helper = getattr(bddown_help, args[0].lower(), bddown_help.help)
        usage(helper)
    elif len(args) == 0:
        usage(bddown_help.show_help)
    else:
        usage(bddown_help.help)


def usage(doc=bddown_help.usage, message=None):
    if hasattr(doc, '__call__'):
        doc = doc()
    if message:
        print message
    print doc.strip()