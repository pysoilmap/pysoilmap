import pysoilmap.shapeops as shapeops

import geopandas as gpd
import pytest
import shapely
from numpy.testing import assert_allclose


# TODO checks:
# - repair(invalid shapes)
# - repair(more complex shapes)
# - repair(repair(shape)) = repair(shape) (?)
# - buffer(more complex shapes)


def test_repair_valid_rectangle():
    """Check that ``repair`` does nothing for a valid rectangle."""
    gdf = gpd.GeoDataFrame(geometry=[
        shapely.geometry.box(0, 1, 2, 3),
        shapely.geometry.box(3, 1, 4, 2),
    ])
    out = shapeops.repair(gdf)
    assert isinstance(out, gpd.GeoDataFrame)
    assert out is not gdf
    assert out.is_valid.all()
    assert all([
        input_shape.equals(output_shape)
        for input_shape, output_shape in zip(gdf.geometry, out.geometry)
    ])


@pytest.mark.parametrize('distance', [
    0.0, -0.0, 0,
    0.1, 0.4, 1.0, 1234,
    -0.1, -0.4,
])
def test_buffer_rectangle(distance):
    gdf = gpd.GeoDataFrame(geometry=[
        shapely.geometry.box(0, 1, 2, 3),
        shapely.geometry.box(3, 1, 4, 2),
    ])

    out = shapeops.buffer(gdf, distance)
    assert isinstance(out, gpd.GeoDataFrame)
    assert out is not gdf
    assert out.is_valid.all()
    assert_allclose(out.bounds.minx, gdf.bounds.minx - distance)
    assert_allclose(out.bounds.miny, gdf.bounds.miny - distance)
    assert_allclose(out.bounds.maxx, gdf.bounds.maxx + distance)
    assert_allclose(out.bounds.maxy, gdf.bounds.maxy + distance)
