"""
Utilities for Google Earth Engine API.
"""

import ee
import folium
import jinja2
import numpy as np

import io
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
):
    """
    Download a small image (<=50MB) from Google Earth Engine API.

    :param: bands

    Note that ``transform`` defines

    ``transform`` should be: [xmin, 0, xscale, 0, -yscale, ymax]
    """
    result = load_image(image, **{
        'bands': [bands] if isinstance(bands, str) else bands,
        'crs': crs,
        'crs_transform': transform,
        'dimensions': [xdim, ydim],
        'format': format,
    })
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
    """Calculate potential locations of cloud shadows."""
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
