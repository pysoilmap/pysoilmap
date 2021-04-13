"""
Perform operations on shapefiles.

Usage:
    pysoilmap shapefile info <input>
    pysoilmap shapefile repair <input> [-o FILE|--inplace]
    pysoilmap shapefile buffer <input> <distance> [-o FILE|--inplace]

Options:
   -o FILE, --output FILE       Output file
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

    if opts['repair'] or opts['buffer']:
        if opts['--inplace']:
            out_fname = in_fname

        if not out_fname:
            print("Missing output file name. You must specify either "
                  "'--output' or '--inplace'!")
            return 1

    print("Reading shapefile: {}".format(in_fname))
    try:
        gdf = gpd.read_file(in_fname)
    except Exception as e:
        print(e)
        return 1

    if opts['info']:
        gdf.info(verbose=True, show_counts=True)

    elif opts['buffer']:
        try:
            distance = float(opts['<distance>'])
        except ValueError:
            print("Expected number for '--buffer DISTANCE', got: {!r}".format(
                opts['--buffer']
            ))
            return 1
        print("Buffering geometries…")
        gdf = shapeops.buffer(gdf, distance)

    elif opts['repair']:
        print("Repairing geometries…")
        gdf = shapeops.repair(gdf)

    if out_fname:
        print("Writing to: {}".format(out_fname))
        gdf.to_file(out_fname)
    return 0
