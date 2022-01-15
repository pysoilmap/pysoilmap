"""
Utilities for Google Earth Engine API.
"""

import ee
import numpy as np

import io
import os
from urllib.request import urlopen


def initialize():
    """Initialize Google Earth Engine.

    Authenticate if necessary, otherwise reuse existing credentials.

    Logs in using a Service Account if etiher of the environment variables
    EE_KEY_DATA or EE_KEY_FILE is set.

    See [1] for infos on setting up a service account.

    [1]: https://developers.google.com/earth-engine/guides/service_account
    """
    key_data = os.environ.get('EE_KEY_DATA')
    key_file = os.environ.get('EE_KEY_FILE')
    if key_data or key_file:
        ee.Initialize(ee.ServiceAccountCredentials(None, key_file, key_data))
        return
    try:
        ee.Initialize()
    except ee.EEException:
        ee.Authenticate()
        ee.Initialize()


def download_image(
    image: ee.Image,
    *,
    band: str,
    crs: str,
    transform: list,
    xdim: int,
    ydim: int,
    format: str = 'NPY',
):
    """
    Download a small image (<=50MB) from Google Earth Engine API.

    :param: bands

    Note that ``transform`` defines

    ``transform`` should be: [xmin, 0, xscale, 0, -yscale, ymax]
    """
    result = load_image(image, **{
        'bands': [band],
        'crs': crs,
        'crs_transform': transform,
        'dimensions': [xdim, ydim],
        'format': format,
    })
    if isinstance(result, np.ndarray):
        return result[band]
    else:
        return result


def load_image(image, **kwargs):
    fmt = kwargs.setdefault('format', 'NPY')
    url = image.getDownloadUrl(kwargs)
    with urlopen(url) as f:
        data = f.read()
    if fmt == 'NPY':
        return np.load(io.BytesIO(data))
    else:
        return data


def add_map_layer(
    self,
    image: ee.Image,
    vis_params: dict = None,
    name: str = None,
    show: bool = True,
    opacity: float = 1,
    min_zoom: int = 0,
):
    """Add an image layer to a :class:`folium.Map`."""
    import folium
    if vis_params is None:
        vis_params = vis(image)
    if name is None:
        name = ', '.join(image.bandNames().getInfo())
    attribution = (
        'Map Data &copy; <a href="https://earthengine.google.com/">'
        'Google Earth Engine</a>')
    tiles = image.getMapId(vis_params)['tile_fetcher']
    folium.raster_layers.TileLayer(
        tiles=tiles.url_format,
        attr=attribution,
        name=name,
        show=show,
        opacity=opacity,
        min_zoom=min_zoom,
        overlay=True,
        control=True,
    ).add_to(self)


def vis(img: ee.Image, bands: list = None) -> dict:
    """Return visualization parameters for the given image."""
    bands = bands or img.bandNames().getInfo()
    reducer = ee.Reducer.percentile([1, 99], ['min', 'max'])
    quantiles = img.reduceRegion(reducer, scale=90, bestEffort=True).getInfo()
    return {
        'min': [quantiles[b + '_min'] for b in bands],
        'max': [quantiles[b + '_max'] for b in bands],
    }


def center(image: ee.Image) -> list:
    """Center a folium.Map on a given Image."""
    return image.geometry().centroid(10).coordinates().reverse().getInfo()
