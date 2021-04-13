"""
Show help on a pysoilmap command or show a list of all available commands.

Usage:
    pysoilmap help [<command>]


See 'pysoilmap help' for a list of all available commands.
"""

from docopt import docopt

from importlib import import_module
import sys


def main(args=None):
    """Show pysoilmap command line help."""
    if args is None:
        args = sys.argv[1:]

    opts = docopt(__doc__, ['help'] + args)

    if opts['<command>']:
        modname = 'pysoilmap.cli.' + opts['<command>']
    else:
        modname = 'pysoilmap.cli'

    module = import_module(modname)
    usage = module.__doc__
    print(usage)
    return 0
