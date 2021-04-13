"""
Perform operations on shapefiles.

Usage:
    pysoilmap shapefile <input> [options] [--inplace|-o FILE]

Options:
   -o FILE, --output FILE       Output file
   --repair                     Attempt to repair broken geometries
                                (no guarantees)
   --buffer DISTANCE            Create buffer around each shape
   --inplace                    Use input file as output file
"""

import pysoilmap.shapeops as shapeops

from docopt import docopt
import geopandas as gpd

import sys


def main(args=None):
    """Show pysoilmap command line help."""
    if args is None:
        args = sys.argv[1:]

    opts = docopt(__doc__, ['shapefile'] + args)

    in_fname = opts['<input>']
    out_fname = opts['--output']
    if opts['--inplace']:
        out_fname = in_fname

    if not out_fname:
        print("Missing output file name. You must specify either '--output' "
              "or '--inplace'!")
        return 1

    print("Reading shapefile: {}".format(in_fname))
    try:
        gdf = gpd.read_file(in_fname)
    except Exception as e:
        print(e)
        return 1

    if opts['--buffer'] is not None:
        try:
            distance = float(opts['--buffer'])
        except ValueError:
            print("Expected number for '--buffer DISTANCE', got: {!r}".format(
                opts['--buffer']
            ))
            return 1
        print("Buffering geometries…")
        gdf = shapeops.buffer(gdf, distance)

    if opts['--repair']:
        print("Repairing geometries…")
        gdf = shapeops.repair(gdf)

    print("Writing to: {}".format(out_fname))
    gdf.to_file(out_fname)
    return 0
