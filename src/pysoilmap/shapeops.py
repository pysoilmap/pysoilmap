"""
Operations on GeoDataFrame.
"""

import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Polygon, MultiPoint
import shapely

import os


def clip(gdf: GeoDataFrame, shape: Polygon) -> GeoDataFrame:
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


def read_shape(spec: str) -> Polygon:
    """
    Parse shape from WKT, or bounds, or .wkt or .wkb file.

    :param spec: a string specifying either 'minx,miny,maxx,maxy', or a WKT
                 text, or a filename pointing to a .wkt or .wkb file.
    """
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
    raise ValueError("Unknown shape definition: {!r}".format(spec))


def read_wkt(filename: str) -> Polygon:
    """Read .wkt file."""
    with open(filename, 'rt') as f:
        return shapely.wkt.load(f)


def read_wkb(filename: str) -> Polygon:
    """Read .wkb file."""
    with open(filename, 'rb') as f:
        return shapely.wkb.load(f)


def write_wkt(filename: str, shape: Polygon):
    """Read .wkt file."""
    with open(filename, 'wt') as f:
        shapely.wkt.dump(shape, f)


def write_wkb(filename: str, shape: Polygon):
    """Read .wkb file."""
    with open(filename, 'wb') as f:
        shapely.wkb.dump(shape, f)


def is_point_in_polygon(polygon: Polygon, points: np.ndarray) -> np.ndarray:
    """
    Check which points are contained in a general polygon.

    This may be more efficient than
    ``polygon.intersection(MultiPoint(points))`` if the polygon's Delaunay
    triangulation consists of only few partitions.

    :param polygon: a triangle
    :param points: an ``(N, 2)`` coordinate array.
    :return: a boolean ``(N,)`` array
    """
    # In general, we could also use any other convex partitioning algorithm
    # combined with is_point_in_convex_polygon, but I couldn't find any such
    # implementations in shapely.
    triangles = shapely.ops.triangulate(polygon)
    return np.any([
        is_point_in_triangle(triangle, points)
        for triangle in triangles
    ], axis=0)


def is_point_in_convex_polygon(
        polygon: Polygon,
        points: np.ndarray
        ) -> np.ndarray:
    """
    Check which points are contained in a convex polygon.

    This may be more efficient than
    ``polygon.intersection(MultiPoint(points))`` if the polygon has a low
    number of edges.

    :param polygon: a triangle
    :param points: an ``(N, 2)`` coordinate array.
    :return: a boolean ``(N,)`` array
    """
    mask = is_point_in_bounds(polygon.bounds, points)
    points = points[mask]

    centroid = np.array(polygon.centroid)
    xmin, ymin, xmax, ymax = polygon.bounds
    scale = np.array([xmax - xmin, ymax - ymin])
    points = (np.array(points)[None, :, :] - centroid) / scale
    coords = (np.array(polygon.boundary)[:, None, :] - centroid) / scale
    cross = np.cross(
        coords[1:] - coords[:-1],
        points - coords[:-1])

    result = (
        np.all(cross <= 0, axis=0) |
        np.all(cross >= 0, axis=0))

    mask[mask] = result
    return mask


def is_point_in_triangle(polygon: Polygon, points: np.ndarray) -> np.ndarray:
    """
    Check which points are contained in a triangle.

    :param polygon: a triangle
    :param points: an ``(N, 2)`` coordinate array.
    :return: a boolean ``(N,)`` array
    """
    corners = np.array(polygon.boundary)[:-1]
    if corners.shape[0] != 3:
        raise ValueError(
            "Expected triangle, got polygon with {} boundary points"
            .format(corners.shape[0]))
    A, B, C = corners
    AP = np.array(points) - A
    AB = B - A
    AC = C - A
    v_x = np.cross(AP, AC)
    v_y = np.cross(AB, AP)
    v_z = np.cross(AB, AC)
    return (
        ((v_x >= 0) & (v_y >= 0) & (v_x + v_y <= v_z)) |
        ((v_x <= 0) & (v_y <= 0) & (v_x + v_y >= v_z))
    )


def is_point_in_bounds(bounds: tuple, points: np.ndarray) -> np.ndarray:
    """
    Check which points are contained in the given bounds.

    :param bounds: a tuple ``(minx, miny, maxx, maxy)``
    :param points: an ``(N, 2)`` coordinate array.
    :return: a boolean ``(N,)`` array
    """
    return np.all(
        (points >= bounds[:2]) &
        (points <= bounds[2:]),
        axis=-1)


def find_polygon_at_point(gdf: GeoDataFrame, points: np.ndarray) -> np.ndarray:
    """
    For each point in ``points`` look up the index of a containing polygon in
    a GeoDataFrame, or ``-1`` if none is found.

    :param gdf: a GeoDataFrame whose geometry is queried against
    :param points: an ``(N, 2)`` coordinate array.
    :return: an integer ``(N,)`` array
    """
    # This seems to be slightly slower than using shapely.strtree.STRtree,
    # but it is a bit more natural and simpler.
    index = gdf.sindex
    shapes = gdf.geometry.iloc
    return np.array([
        next((
            i for i in index.query(p)
            if shapes[i].intersects(p)), -1)
        for p in MultiPoint(points[:, :2])
    ])
