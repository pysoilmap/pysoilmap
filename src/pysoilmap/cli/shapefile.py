"""
Perform operations on shapefiles.

Usage:
    pysoilmap shapefile info <input>
    pysoilmap shapefile export <input> [-o FILE]
    pysoilmap shapefile repair <input> [-o FILE|--inplace]
    pysoilmap shapefile buffer <input> <distance> [-o FILE|--inplace]

Options:
   -o FILE, --output FILE       Output file
   --inplace                    Use input file as output file
"""

import pysoilmap.shapeops as shapeops

from docopt import docopt
import geopandas as gpd

import os
import sys


def main(args=None):
    """Show pysoilmap command line help."""
    if args is None:
        args = sys.argv[1:]

    opts = docopt(__doc__, ['shapefile'] + args)

    in_fname = opts['<input>']
    out_fname = opts['--output']

    if opts['export'] or opts['repair'] or opts['buffer']:
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

    elif opts['export']:
        ext = os.path.splitext(out_fname)[1].lower()
        if ext in ('.txt', '.tsv'):
            print("Writing to: {}".format(out_fname))
            gdf.to_csv(out_fname, sep='\t')
        elif ext == '.csv':
            print("Writing to: {}".format(out_fname))
            gdf.to_csv(out_fname)
        else:
            print("Unknown output file extension: {!r}".format(out_fname))
            return 1

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
        print("Writing to: {}".format(out_fname))
        gdf.to_file(out_fname)

    elif opts['repair']:
        print("Repairing geometries…")
        gdf = shapeops.repair(gdf)
        print("Writing to: {}".format(out_fname))
        gdf.to_file(out_fname)

    return 0
