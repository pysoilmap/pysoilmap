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
