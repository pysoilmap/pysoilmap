"""
Show help on a pysoilmap command or show a list of all available commands.
"""

import pysoilmap.cli as cli

import click


@click.command('help', context_settings={'ignore_unknown_options': True})
@click.argument('command', nargs=-1)
def main(command):
    """Show pysoilmap command line help."""
    cli.main(command + ('--help',))
