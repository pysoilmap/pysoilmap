"""
Operations on GeoDataFrame.
"""

from geopandas import GeoDataFrame
from shapely.geometry import Polygon
import shapely

import os


def clip(gdf: GeoDataFrame, shape: Polygon):
    """
    Clip a GeoDataFrame to the specified area.

    Same as (but somewhat faster than) :func:`geopandas.clip` or
    :func:`geopandas.overlay` with ``how='intersection'``.
    """
    ix = gdf.sindex.query(shape, predicate="intersects")
    ix.sort()
    gdf = gdf.iloc[ix]
    gdf = gdf.set_geometry(gdf.geometry.intersection(shape))
    return gdf[~gdf.is_empty]


def repair(gdf: GeoDataFrame) -> GeoDataFrame:
    """
    Attempt to fix broken geometries in the given GeoDataFrame, and returns
    a new GeoDataFrame.

    This uses the ``unary_union()`` as well as the ``buffer(0)`` trick. Your
    mileage may vary.
    """
    return gdf.set_geometry([
        shapely.ops.unary_union([shape])
        for shape in gdf.geometry.buffer(0.0)
    ])


def buffer(
        gdf: GeoDataFrame,
        distance: float = 0.0,
        *args, **kwargs
        ) -> GeoDataFrame:
    """
    Applies ``shape.buffer(...)`` to each shape in a GeoDataFrame and returns
    a new GeoDataFrame with replaced geometry.

    This can be used as a trick to repair some types of broken geometries in
    shapefiles.
    """
    return gdf.set_geometry(
        gdf.geometry.buffer(distance))


def read_shape(spec):
    """Parse shape from WKT, or bounds, or .wkt or .wkb file."""
    if os.path.exists(spec):
        ext = os.path.splitext(spec)[1].lower()
        if ext == '.wkt':
            return read_wkt(spec)
        elif ext == '.wkb':
            return read_wkb(spec)
        try:
            return read_wkt(spec)
        except shapely.errors.ReadingError:
            pass
        try:
            return read_wkb(spec)
        except shapely.errors.ReadingError:
            pass
        raise ValueError("Unknown shape file format: {!r}".format(spec))
    if isinstance(spec, str):
        try:
            minx, miny, maxx, maxy = map(float, spec.split(','))
            return shapely.geometry.box(minx, miny, maxx, maxy)
        except ValueError:
            pass
        try:
            return shapely.wkt.loads(spec)
        except shapely.errors.ReadingError:
            pass
    elif isinstance(spec, bytes):
        return shapely.wkb.loads(spec)
    raise ValueError("Unknown shape definition: {!r}".format(spec))


def read_wkt(filename):
    """Read .wkt file."""
    with open(filename, 'rt') as f:
        return shapely.wkt.load(f)


def read_wkb(filename):
    """Read .wkb file."""
    with open(filename, 'rb') as f:
        return shapely.wkb.load(f)


def write_wkt(filename, shape):
    """Read .wkt file."""
    with open(filename, 'wt') as f:
        return shapely.wkt.dump(shape, f)


def write_wkb(filename, shape):
    """Read .wkb file."""
    with open(filename, 'wb') as f:
        return shapely.wkb.dump(shape, f)
