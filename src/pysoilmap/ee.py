"""
Utilities for Google Earth Engine API.
"""

import ee
import folium
import jinja2
import numpy as np

import io
import math
import os
import urllib.request


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
    bands: "str | list" = None,
    *,
    crs: str,
    transform: list,
    xdim: int,
    ydim: int,
    format: str = 'NPY',
    xtile: int = 1,
    ytile: int = 1,
    threads: int = 1,
):
    """
    Download a small image (<=50MB) from Google Earth Engine API.

    :param bands: list of band names to download
    :param crs: name of the coordinate system
    :param transform: ``[xscale, xshear, xoffs, yshear, yscale, yoffs]``
    :param xdim: image width in pixels
    :param ydim: image height in pixels
    :param format: file format, leave as 'NPY' for now!
    :param xtile: download image in ``xtile * ytile`` pieces
    :param ytile: download image in ``xtile * ytile`` pieces
    :param threads: number of threads for tiled download

    Note that ``transform`` defines the transformation of ``(col, row)`` to
    coordinates. In order to have the (0, 0) pixel in the upper left corner
    ``transform`` should be: ``[xmin, 0, xscale, 0, -yscale, ymax]``.
    """
    if xtile * ytile == 1:
        result = load_image(image, **{
            'bands': [bands] if isinstance(bands, str) else bands,
            'crs': crs,
            'crs_transform': transform,
            'dimensions': [xdim, ydim],
            'format': format,
        })
    else:
        with _ThreadPool(threads) as pool:
            tile_width = math.ceil(xdim / xtile)
            tile_height = math.ceil(ydim / ytile)
            xscale, xshear, xoffs, yshear, yscale, yoffs = transform

            def make_tile(row, col):
                tile_xdim = min(tile_width, xdim - col)
                tile_ydim = min(tile_height, ydim - row)
                tile_xoffs = xscale * col + xshear * row + xoffs
                tile_yoffs = yscale * row + yshear * col + yoffs
                tile_trans = [
                    xscale, xshear, tile_xoffs,
                    yshear, yscale, tile_yoffs,
                ]
                return load_image(image, **{
                    'bands': [bands] if isinstance(bands, str) else bands,
                    'crs': crs,
                    'crs_transform': tile_trans,
                    'dimensions': [tile_xdim, tile_ydim],
                    'format': format,
                })
            tiles = pool.starmap(make_tile, [
                (i * tile_height, j * tile_width)
                for i in range(ytile)
                for j in range(xtile)
            ])
        result = np.block([
            tiles[xtile * row:xtile * (row + 1)]
            for row in range(ytile)
        ])
    if isinstance(result, np.ndarray) and isinstance(bands, str):
        return result[bands]
    else:
        return result


def load_image(image, **kwargs):
    fmt = kwargs.setdefault('format', 'NPY')
    url = image.getDownloadUrl(kwargs)
    with urllib.request.urlopen(url) as f:
        data = f.read()
    if fmt == 'NPY':
        return np.load(io.BytesIO(data))
    else:
        return data


def add_map_layer(
    self: folium.Map,
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


def vis(img: ee.Image, bands: list = None, region: ee.Geometry = None) -> dict:
    """Return visualization parameters for the given image."""
    region = region or img.geometry()
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


class LayerRadioControl(folium.LayerControl):

    """
    Same as folium.LayerControl, but assumes the overlay layers are exclusive
    and the base layers are optional.
    """

    _template = jinja2.Template("""
        {% macro script(this,kwargs) %}
            var {{ this.get_name() }} = {
                base_layers : {
                    {%- for key, val in this.base_layers.items() %}
                    {{ key|tojson }} : {{val}},
                    {%- endfor %}
                },
                overlays :  {
                    {%- for key, val in this.overlays.items() %}
                    {{ key|tojson }} : {{val}},
                    {%- endfor %}
                },
            };
            L.control.layers(
                {{ this.get_name() }}.overlays,
                {{ this.get_name() }}.base_layers,
                {{ this.options|tojson }}
            ).addTo({{this._parent.get_name()}});

            (function(control) {
                Object.keys(control.base_layers).forEach(function(key, idx) {
                    control.base_layers[key].setZIndex(-idx);
                });

                Object.keys(control.overlays).forEach(function(key, idx) {
                    control.overlays[key].setZIndex(idx + 1);
                });
            })({{ this.get_name() }});

            {%- for val in this.layers_untoggle.values() %}
            {{ val }}.remove();
            {%- endfor %}
        {% endmacro %}
        """)


# Author: Gennadii Donchyts
# License: Apache 2.0
def cast_shadows(image: ee.Image, cloud: ee.Image) -> ee.Image:
    """
    Calculate potential locations of cloud shadows.

    Adapted from the 3_Sentinel2_CloudAndShadowMask notebook in:
    https://github.com/rdandrimont/AGREE/
    """
    # solar geometry (radians)
    azimuth = (
        ee.Number(image.get("MEAN_SOLAR_AZIMUTH_ANGLE"))
        .multiply(np.pi / 180.0)
        .add(0.5 * np.pi)
    )
    zenith = (
        ee.Number(0.5 * np.pi)
        .subtract(
            ee.Number(image.get("MEAN_SOLAR_ZENITH_ANGLE"))
            .multiply(np.pi / 180.0)
        )
    )
    # find where cloud shadows should be based on solar geometry
    nominalScale = cloud.projection().nominalScale()

    def change_cloud_projection(cloudHeight):
        shadowVector = zenith.tan().multiply(cloudHeight)
        x = azimuth.cos().multiply(shadowVector).divide(nominalScale).round()
        y = azimuth.sin().multiply(shadowVector).divide(nominalScale).round()
        return cloud.changeProj(
            cloud.projection(),
            cloud.projection().translate(x, y))

    cloudHeights = ee.List.sequence(200, 10000, 500)
    shadows = cloudHeights.map(change_cloud_projection)
    shadows = ee.ImageCollection.fromImages(shadows).max()

    # (modified by Sam Murphy) dark pixel detection
    # B3 = green
    # B12 = swir2
    dark = image.normalizedDifference(["B3", "B12"]).gt(0.25)
    shadows = shadows.And(dark)
    return shadows


class _ThreadPool:

    def __new__(cls, n_threads):
        if n_threads > 1:
            from multiprocessing.pool import ThreadPool
            return ThreadPool(n_threads)
        else:
            return object.__new__(cls)

    def __enter__(self):
        return self

    def __exit__(self, *exc_state):
        pass

    def starmap(self, func, iterable):
        return [func(*item) for item in iterable]
