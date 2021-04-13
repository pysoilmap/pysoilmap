"""
Usage:
    pysoilmap --version
    pysoilmap <command> [<args>...]

Options:
   -v, --version            Print pysoilmap version information

The most commonly used subcommands are:
   help                     Get help
   shapefile                Operations on shapefiles


See 'pysoilmap help <command>' for more information on a specific command.
"""

import pysoilmap

from docopt import docopt
from importlib import import_module


subcommands = [
    'help',
    'shapefile',
]


def main(args=None):
    """
    Execute pysoilmap command. See above for usage options.
    """
    opts = docopt(
        __doc__,
        args,
        version='pysoilmap ' + pysoilmap.__version__,
        options_first=True)

    command = opts['<command>']

    if command in subcommands:
        module = import_module('pysoilmap.cli.' + command)
        exitcode = module.main(opts['<args>'])
        return exitcode

    else:
        print("Unknown subcommand: {!r}!".format(command))
        return 1
