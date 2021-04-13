"""
Perform operations on shapefiles.
"""

import pysoilmap.shapeops as shapeops

import click
import geopandas as gpd

import os


@click.group('shapefile')
def main(args=None):
    """Execute shapefile command."""
    pass


@main.command()
@click.argument('input_file')
def info(input_file):
    """Show info about shapefile and its columns."""
    gdf = _read_shapefile(input_file)
    gdf.info(verbose=True, show_counts=True)


@main.command()
@click.option('-o', '--output', 'output_file')
@click.argument('input_file')
def export(input_file, output_file):
    """Export shapefile data columns to .csv or .tsv."""
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in ('.txt', '.tsv', '.csv'):
        raise click.ClickException(
            "Unknown output file extension: {!r}".format(output_file))

    gdf = _read_shapefile(input_file)
    if ext in ('.txt', '.tsv'):
        print("Writing to: {}".format(output_file))
        gdf.to_csv(output_file, sep='\t')
    elif ext == '.csv':
        print("Writing to: {}".format(output_file))
        gdf.to_csv(output_file)


@main.command()
@click.argument('input_file')
@click.argument('distance', type=float)
@click.option('-o', '--output', 'output_file', help='Output file')
@click.option('--inplace', is_flag=True, help='Use input file as output file')
def buffer(input_file, output_file, distance: float, inplace):
    """Apply ``shape.buffer(...)`` to each shape in a shapefile."""
    print(output_file, inplace)
    if inplace:
        if output_file is not None:
            raise click.UsageError("--inplace is incompatible with --output!")
        output_file = input_file
    elif output_file is None:
        raise click.UsageError(
            "Missing output file name. You must specify either "
            "'--output' or '--inplace'!")

    gdf = _read_shapefile(input_file)
    print("Buffering geometries…")
    gdf = shapeops.buffer(gdf, distance)
    _write_shapefile(gdf, output_file)


@main.command()
@click.argument('input_file')
@click.option('-o', '--output', 'output_file', help='Output file')
@click.option('--inplace', is_flag=True, help='Use input file as output file')
def repair(input_file, output_file, inplace):
    """Attempt to fix broken geometries in the given shapefile."""
    if inplace:
        if output_file is not None:
            raise click.UsageError("--inplace is incompatible with --output!")
        output_file = input_file
    elif output_file is None:
        raise click.UsageError(
            "Missing output file name. You must specify either "
            "'--output' or '--inplace'!")
    gdf = _read_shapefile(input_file)
    print("Repairing geometries…")
    gdf = shapeops.repair(gdf)
    _write_shapefile(gdf, output_file)


def _read_shapefile(filename):
    """Read shapefile."""
    print("Reading shapefile: {}".format(filename))
    try:
        return gpd.read_file(filename)
    except Exception as e:
        raise click.ClickException(e)


def _write_shapefile(gdf, filename):
    """Write shapefile."""
    print("Writing to: {}".format(filename))
    gdf.to_file(filename)
