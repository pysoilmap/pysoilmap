# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: py:light,ipynb
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Cloud mask in the Sentinel-2 data
#
# This is a short demo of the cloud mask in the sentinel-2 dataset.
#
# For a more sophisticated method of dealing with clouds, see the
# [Sentinel-2 Cloud Masking with s2cloudless][1] example.
#
# [1]:
# https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless

import ee
import folium
import pysoilmap.ee as psee

psee.initialize()

# The full dataset and documentation is available here:
#
# https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2
#
# When using a dataset, always make sure to refer to the documentation
# for resolution, band names and definitions, etc.
#
# For the purpose of this example, we'll select a specific image
# taken on a specific flyover to keep the computation time short:

img = ee.Image("COPERNICUS/S2/20180430T103019_20180430T103520_T32UMU")
rgb = img.select(["B2", "B3", "B4"]).divide(10_000)

# Bits 10 and 11 are opaque and cirrus clouds, respectively:

clouds = img.select('QA60').bitwiseAnd(0xc00)
opaque = clouds.bitwiseAnd(0x400)
cirrus = clouds.bitwiseAnd(0x800)
shad_o = psee.cast_shadows(img, opaque)
shad_c = psee.cast_shadows(img, cirrus)

# These derived images can now be added in javascript using
# [Map.addLayer()][1] or in python using e.g. [geemap.Map.addLayer()][2].
#
# [1]: https://developers.google.com/earth-engine/apidocs/map-addlayer
# [2]: https://geemap.org/geemap/#geemap.geemap.Map.addLayer
#
# For the purpose of this notebook, we'll add it to a
# `folium.Map` using `pysoilmap.ee.add_map_layer()`:

folium.Map.addLayer = psee.add_map_layer

mask = (lambda mask: mask.updateMask(mask.neq(0)))
vis = (lambda color: {'min': 0, 'max': 1, 'palette': color})

Map = folium.Map(location=psee.center(img), zoom_start=9)
Map.addLayer(rgb, {'min': 0, 'max': 0.3}, "RGB")
Map.addLayer(mask(opaque), vis('yellow'), name="Opaque Clouds")
Map.addLayer(mask(cirrus), vis('red'), name="Cirrus Clouds")
Map.addLayer(mask(shad_o), vis('teal'), name="Opaque Shadows")
Map.addLayer(mask(shad_c), vis('pink'), name="Cirrus Shadows")
Map.add_child(folium.LayerControl())
Map
