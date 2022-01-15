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

# # Spectral indices from Sentinel-2 data
#
# This is a short demo that shows how to download Sentinel-2 data and
# compute several spectral indices.

import ee
import folium
import pysoilmap.ee as psee

psee.initialize()

# ### Sentinel-2 data
#
# The full dataset and documentation is available here:
#
# https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2
#
# When using a dataset, always make sure to refer to the documentation
# for resolution, band names and definitions, etc.
#
# The following app is very useful to identify images with only
# few clouds during a desired time interval:
#
# https://showcase.earthengine.app/view/s2-sr-browser-s2cloudless-nb
#
# For the purpose of this example, we'll select a specific image
# taken on a specific flyover to keep the computation time short.
# A more advanced use case

img = ee.Image("COPERNICUS/S2/20180427T102019_20180427T102022_T32UNU")
img = img.divide(10_000)

# We'll calculate a selection of derived variables based on the
# RGB and near-infrared bands, according to Table 2 in [^1]:
#
# | Name                                   | Var   | Formula                 |
# |:---------------------------------------|:------|:------------------------|
# | Brightness Index                       | BI    | √(R² + G² + B²) / √3    |
# | Saturation Index                       | SI    | (R - B) / (R + B)       |
# | Hue Index                              | HI    | (2·R - G - B) / (G - B) |
# | Coloration Index                       | CI    | (R - G) / (R + G)       |
# | Redness Index                          | RI    | R² / (B·G³)             |
# | Normalized Difference Vegatation Index | NDVI  | (NIR - R) / (NIR + R)   |
#
# [^1]: Hounkpatin, et al., 2018, Predicting reference soil groups using
#       legacy data: A data pruning and Random Forest approach for tropical
#       environment (Dano catchment, Burkina Faso)

RGB = img.select(["B4", "B3", "B2"])
NIR = img.select("B8")
R = img.select("B4")
G = img.select("B3")
B = img.select("B2")

BI = R.pow(2).add(G.pow(2)).add(B.pow(2)).divide(3).sqrt()
SI = R.subtract(B).divide(R.add(B))
CI = R.subtract(G).divide(R.add(G))
RI = R.pow(2).divide(B.multiply(G.pow(3)))
HI = R.multiply(2).subtract(G).subtract(B).divide(G.subtract(B))
NDVI = NIR.subtract(R).divide(NIR.add(R))

# These derived images can now be added in javascript using
# [Map.addLayer()](https://developers.google.com/earth-engine/apidocs/map-addlayer)
# or in python using e.g.
# [geemap.Map.addLayer()](https://geemap.org/geemap/#geemap.geemap.Map.addLayer).
#
# For the purpose of this notebook, we'll add it to a
# `folium.Map` using `pysoilmap.ee.add_map_layer()`:

folium.Map.addLayer = psee.add_map_layer

Map = folium.Map(location=psee.center(img), zoom_start=9)
Map.addLayer(RGB, {'min': 0, 'max': 0.3}, "RGB")
Map.addLayer(BI, name="Brightness Index")
Map.addLayer(SI, name="Saturation Index")
Map.addLayer(CI, name="Coloration Index")
Map.addLayer(RI, name="Redness Index")
Map.addLayer(HI, name="Hue Index")
Map.addLayer(NDVI, name="NDVI")
Map.add_child(folium.LayerControl())
Map
