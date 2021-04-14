"""
Perform operations on shapefiles.
"""

import pysoilmap.shapeops as shapeops

import click
import geopandas as gpd

import functools
import os


def needs_gdf(func):
    """Marks a callback as wanting to receive the current GeoDataFrame
    object as first argument."""
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context().find_root()
        gdf = ctx.obj
        if gdf is None:
            raise click.ClickException(
                f"Please use `read <file>` before the '{ctx.command.name}' "
                "command!")
        return func(gdf, *args, **kwargs)
    return functools.update_wrapper(wrapper, func)


def returns_gdf(func):
    """Marks a callback as returning the new GeoDataFrame object."""
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context().find_root()
        ctx.obj = func(*args, **kwargs)
        return ctx.obj
    return functools.update_wrapper(wrapper, func)


@click.group(
    'shapefile',
    chain=True,
    no_args_is_help=True,
    subcommand_metavar='(<command> [<args>...])...',
)
def main():
    """Execute shapefile command."""
    pass


@main.command()
@click.argument('file', metavar='<file>')
@returns_gdf
def read(file):
    """Read shapefile - always lead with this command!"""
    print("Reading shapefile: {}".format(file))
    try:
        return gpd.read_file(file)
    except Exception as e:
        raise click.ClickException(e)


@main.command()
@click.argument('file', metavar='<file>')
@needs_gdf
def write(gdf, file):
    """
    Write shapefile. You should usually close with this command.

    Note that in addition to '.shp' can can also write to '.csv', '.tsv', or
    '.txt'. In this case, only the row data without shape information will be
    exported.
    """
    print("Writing to: {}".format(file))
    ext = os.path.splitext(file)[1].lower()
    if ext in ('.txt', '.tsv'):
        gdf.to_csv(file, index=False, sep='\t')
    elif ext == '.csv':
        gdf.to_csv(file, index=False)
    else:
        gdf.to_file(file)


@main.command()
@needs_gdf
def info(gdf):
    """Show info about shapefile and its columns."""
    gdf.info(verbose=True, show_counts=True)


@main.command()
@click.argument('distance', metavar='<distance>', type=float)
@returns_gdf
@needs_gdf
def buffer(gdf, distance: float):
    """Apply ``shape.buffer(...)`` to each shape in a shapefile."""
    print("Buffering geometries…")
    return shapeops.buffer(gdf, distance)


@main.command()
@returns_gdf
@needs_gdf
def repair(gdf):
    """Attempt to fix broken geometries in the given shapefile."""
    print("Repairing geometries…")
    return shapeops.repair(gdf)


@main.command()
@click.argument('crs', metavar='<crs>')
@returns_gdf
@needs_gdf
def to_crs(gdf, crs):
    """Reproject to a new CRS."""
    print("Reprojecting to CRS: {}".format(crs))
    return gdf.to_crs(crs)


@main.command()
@click.argument('crs', metavar='<crs>')
@returns_gdf
@needs_gdf
def set_crs(gdf, crs):
    """Assign new CRS without reprojection."""
    print("Assigning CRS: {}".format(crs))
    return gdf.set_crs(crs)


@main.command()
@click.argument('shape', metavar='<shape>')
@returns_gdf
@needs_gdf
def clip(gdf, shape):
    """
    Clip GeoDataFrame to specified shape. The shape can be given as bounds,
    WKT, or .wkt or .wkb file.
    """
    try:
        shape = shapeops.read_shape(shape)
    except ValueError as e:
        raise click.ClickException(str(e))
    return shapeops.clip(gdf, shape)
