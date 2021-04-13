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

import click
from importlib import import_module


class SubCommands(click.MultiCommand):

    def __init__(self, *args, package, commands, **kwargs):
        super().__init__(*args, **kwargs)
        self._package = package
        self._commands = commands

    def list_commands(self, ctx):
        return self._commands

    def get_command(self, ctx, name):
        if name in self._commands:
            module = import_module(self._package + '.' + name)
            return module.main


@click.command(
    'pysoilmap',
    cls=SubCommands,
    package='pysoilmap.cli',
    commands=[
        'shapefile',
        'help',
    ],
)
@click.version_option(
    version=pysoilmap.__version__,
    prog_name='pysoilmap',
)
def main():
    pass
