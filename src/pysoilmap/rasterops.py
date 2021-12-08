"""
Utility functions for working with rasterized data and, more specifically,
:class:`xarray.DataArray`.
"""

import geopandas as gpd
import numpy as np
import rasterio as rio
import rasterio.features as riof
import xarray as xr
from affine import Affine


def rasterize_like(
    like: xr.DataArray,
    polygons: gpd.GeoSeries,
    values: np.ndarray,
    nodata=-1,
) -> np.ndarray:
    """
    Rasterize polygon values like the given raster array.

    This function uses :func:`rasterio.features.rasterize` under the hood and
    extends its functionality to:

        1. handle non-numeric data (such as arrays of string values), and
        2. allow rasterizing multiple channels at once

    :param like: raster with the target shape and transform
    :param polygons: 1D array of N polygons
    :param values: ``(*C, N)`` array of corresponding values
    :param nodata: nodata value.
    """
    # TODO: make this work with value dicts
    # TODO: handle heterogeneous arrays
    # TODO: return xr.DataArray(?)
    indices = riof.rasterize(
        zip(polygons, np.arange(len(polygons))),
        out_shape=like.shape[-2:],
        transform=get_transform(like),
        fill=-1)
    nodata = np.reshape(nodata, (*np.shape(nodata), 1))
    values = np.concatenate((values, nodata), axis=-1)
    output = np.take(values, indices.ravel(), -1)
    return output.reshape(values.shape[:-1] + indices.shape)


def write_tiff(fname, data, like, names=None, nodata=-1):
    """
    Write numpy array to a GeoTIFF file.

    :param fname: file name
    :param data: ``(…, NY, NX)`` array of data
    :param like: a (…, NY, NX)`` data array
    :param names: band names (optional)
    :param nodata: nodata value
    """
    data = np.as_array(data)
    data = data.reshape(-1, *data.shape[-2:])
    with rio.open(
        fname, 'w',
        driver='GTiff',
        count=data.shape[0],
        height=data.shape[1],
        width=data.shape[2],
        crs=like.crs,
        transform=get_transform(like),
        dtype=data.dtype,
        nodata=nodata
    ) as f:
        for i, x in enumerate(data):
            f.write(x, i + 1)
        if names:
            for i, x in enumerate(names):
                f.set_band_description(i + 1, x)


def get_transform(dataarray: xr.DataArray) -> Affine:
    """
    Return the transform associated with the given raster, or, if unset,
    assume a rectangular grid and create the corresponding transformation.

    :param dataarray: the array for which to return a transformation object
    """
    transform = getattr(dataarray, 'transform', None)
    if transform:
        return transform
    else:
        xs = dataarray.x.values
        ys = dataarray.y.values
        x0 = xs[0]
        dx = xs[1] - x0
        y0 = ys[0]
        dy = ys[1] - y0
        return Affine(
            dx, 0.0, x0 - dx/2,
            0.0, dy, y0 - dy/2)
