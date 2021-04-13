"""
Operations on GeoDataFrame.
"""

from geopandas import GeoDataFrame
import shapely


def repair(gdf: GeoDataFrame) -> GeoDataFrame:
    """
    Attempt to fix broken geometries in the given GeoDataFrame, and returns
    a new GeoDataFrame.

    This uses the ``unary_union()`` as well as the ``buffer(0)`` trick. Your
    mileage may vary.
    """
    return gdf.set_geometry([
        shapely.ops.unary_union([shape.buffer(0.0)])
        for shape in gdf.geometry
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
    return gdf.set_geometry([
        shape.buffer(distance, *args, **kwargs)
        for shape in gdf.geometry
    ])
