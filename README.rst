pysoilmap
=========

|Version| |License| |Docs| |Tests| |Coverage|

Tools for performing Digital Soil Mapping (DSM) with python.

This project aims to provide a high-level user interface and examples for
common tasks related to DSM, accessible through a command line interface or
python APIs. The actual legwork is done by established libraries for numerical
computations, machine-learning, image-processing, geostatistics, projections,
geometries, file-formats, etc. Customized solutions are implemented where
needed or more convenient.


Resources
~~~~~~~~~

This is a list of some useful python packages and other resources in the
context of DSM:

Data formats:

- geopandas_: for vector data (shapefiles, .gpkg, etc.). I recommend saving
  data as .gpkg (not shapefiles) to get a single self-contained file.
- rasterio_: for GeoTIFF files
- xarray_ for NetCDF (.nc) files. It can also read GeoTIFF if rasterio is
  installed.
- (exifread_ can read metadata from TIFFs)
- (pyshp_: read/write raw shapefiles, without the overhead or convenience of
  geopandas)
- (xlrd_ to read excel files via ``pandas.read_excel``)

.. _geopandas: https://pypi.org/project/geopandas/
.. _rasterio: https://pypi.org/project/rasterio/
.. _xarray: https://pypi.org/project/xarray/
.. _pyshp: https://pypi.org/project/pyshp/
.. _exifread: https://pypi.org/project/exifread/
.. _xlrd: https://pypi.org/project/xlrd/

Covariates:

- elevation_: downloads SRTM30/SRTM90 Digital Elevation Models (DEM) for
  arbitrary locations
- pysheds_: watershed delineation
- richdem_: set of DEM hydrologic analysis tools
- xclim_: derived climate variables built with xarray

.. _elevation: https://pypi.org/project/elevation/
.. _pysheds: https://pypi.org/project/pysheds/
.. _richdem: https://pypi.org/project/richdem/
.. _xclim: https://pypi.org/project/xclim/

Google earth:

- earthengine-api_: Google Earth Engine API
- geemap_: interactive mapping (in jupyter) using Google Earth Engine

.. _earthengine-api: https://pypi.org/project/earthengine-api/
.. _geemap: https://pypi.org/project/geemap/

Machine learning:

- scipy_: General purpose scientific library, optimizers, image filters
- scikit-learn_: Many easy-to-use general purpose machine learning algorithms
- PyKrige_: Kriging toolkit
- GPflow_: Gaussian processes in tensorflow
- gpytorch_: Gaussian processes in pytorch
- (scikit-image_: collection of algorithms for image processing)

.. _scipy: https://pypi.org/project/scipy/
.. _scikit-learn: https://pypi.org/project/scikit-learn/
.. _pykrige: https://pypi.org/project/pykrige/
.. _gpflow: https://pypi.org/project/gpflow/
.. _gpytorch: https://pypi.org/project/gpytorch/
.. _scikit-image: https://pypi.org/project/scikit-image/

Coordinates and shapes:

- shapely_: Geometric objects, predicates, and operations
- pyproj_: cartographic projections and coordinate transformations library
- (affine_: affine transformation of the plane. Usually indirectly installed
  through shapely or others)
- (rtree_: spatial indexing, i.e. fast lookup of polygons by coordinates)
- (descartes_: plotting geometric objects with matplotlib)

.. _shapely: https://pypi.org/project/shapely/
.. _pyproj: https://pypi.org/project/pyproj/
.. _affine: https://pypi.org/project/affine/
.. _rtree: https://pypi.org/project/rtree/
.. _descartes: https://pypi.org/project/descartes/

Jupyter:

- jupytext_: command line tool to convert .ipynb to and from different file
  formats (.html, .py), execute a notebook or clear all outputs
- (jupyterlab_: more interactive interface for jupyter notebooks. Warning:
  interactive widgets often work only either in lab or notebook)
- (ipympl_: interactive matplotlib figures for jupyterlab)
- (ipywidgets_: interactive widgets for jupyterlab - progress bar, buttons,
  checkboxes etc)

.. _jupytext: https://pypi.org/project/jupytext/
.. _jupyterlab: https://pypi.org/project/jupyterlab/
.. _ipympl: https://pypi.org/project/ipympl/
.. _ipywidgets: https://pypi.org/project/ipywidgets/

Dataset catalogs:

- `Earth Engine Data Catalog`_: Catalog of various environmental datasets
- `Free GIS Data`_: Large collection of references to datasets
- `Useful Geographic Datasets`_
- `List of GIS data sources`_: wikipedia entry
- `ArcGIS Hub`_
- `EarthExplorer`_

.. _Earth Engine Data Catalog: https://developers.google.com/earth-engine/datasets
.. _Free GIS Data: https://freegisdata.rtwilson.com/
.. _Useful Geographic Datasets: https://jcheshire.com/resources/geographic-datasets/
.. _List of GIS data sources: https://en.wikipedia.org/wiki/List_of_GIS_data_sources
.. _ArcGIS Hub: https://hub.arcgis.com/search
.. _EarthExplorer: https://earthexplorer.usgs.gov/


Features
~~~~~~~~

This project has just been initiated, there are no(t many) features yet.

Features so far:

- (none)


Roadmap
~~~~~~~

In the future, we plan on working the following features:

- common interface for several machine learning models for linear
  regression, kriging, regression-kriging, random forests, ...
- computation of several topographic covariates from DEM (curvatures, slope,
  aspect, radiation angle, ...)
- plotting of raster and vector data
- reprojection, resampling
- sampling points from vector datasets
- custom non-stationary GP kernels for DSM
- algorithms for experimental design (DOE)
- 3D terrain survey
- ...?


Links
~~~~~

- Documentation_
- Releases_
- `Source Code`_
- License_
- Tests_

.. _Documentation: https://pysoilmap.readthedocs.io/en/latest/
.. _Releases: https://pypi.python.org/pypi/pysoilmap
.. _Tests: https://github.com/pysoilmap/pysoilmap/actions/workflows/main.yml
.. _Source Code: https://github.com/pysoilmap/pysoilmap
.. _License: https://github.com/pysoilmap/pysoilmap/blob/main/UNLICENSE


Installation
~~~~~~~~~~~~

Once the first release is available, install via:

.. code-block:: python

    pip install pysoilmap


Usage
~~~~~

TBD



.. Badges:

.. |Version| image::    https://img.shields.io/pypi/v/pysoilmap.svg
   :target:             https://pypi.python.org/pypi/pysoilmap
   :alt:                Latest Release

.. |License| image::    https://img.shields.io/pypi/l/pysoilmap.svg
   :target:             https://github.com/pysoilmap/pysoilmap/blob/main/UNLICENSE
   :alt:                License: Unlicense

.. |Docs| image::       https://readthedocs.org/projects/pysoilmap/badge/?version=latest
   :target:             https://pysoilmap.readthedocs.io/en/latest/?badge=latest
   :alt:                Documentation

.. |Tests| image::      https://github.com/pysoilmap/pysoilmap/actions/workflows/main.yml/badge.svg
   :target:             https://github.com/pysoilmap/pysoilmap/actions/workflows/main.yml
   :alt:                Test status

.. |Coverage| image::   https://coveralls.io/repos/pysoilmap/pysoilmap/badge.svg?branch=main
   :target:             https://coveralls.io/r/pysoilmap/pysoilmap
   :alt:                Coverage
