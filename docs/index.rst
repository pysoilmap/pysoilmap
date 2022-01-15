.. pysoilmap documentation master file, created by
   sphinx-quickstart on Mon Apr 12 14:39:37 2021.

Welcome to pysoilmap's documentation!
=====================================

This project will contain examples and utilities for performing Digital Soil
Mapping (DSM) and related tasks in python.

This project aims to provide examples and utilities for common tasks related
to DSM. For some of these tasks, we also want to work on high-level user
interfaces, accessible via python APIs or the command line. The actual legwork
is done by established libraries for numerical computations, machine-learning,
image-processing, geostatistics, projections, geometries, file-formats, etc.
Custom solutions are implemented where needed or more convenient.

.. _Documentation: https://pysoilmap.readthedocs.io/en/latest/
.. _Releases: https://pypi.python.org/pypi/pysoilmap
.. _Tests: https://github.com/pysoilmap/pysoilmap/actions/workflows/main.yml
.. _Source Code: https://github.com/pysoilmap/pysoilmap
.. _License: https://github.com/pysoilmap/pysoilmap/blob/master/UNLICENSE

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   examples/index
   usage
   api/index


Links
*****

- Documentation_
- Releases_
- `Source Code`_
- License_
- Tests_


Features
********

This project has just been initiated, there are not many features yet.

Features so far:

- computation of several topographic covariates from DEM (curvatures, slope,
  aspect, radiation angle, ...)


Roadmap
~~~~~~~

In the future, we plan on working the following topics:

- common easy-to-use interface (like scikit-learn) for several machine
  learning models for linear regression, kriging, regression-kriging, random
  forests, ...
- examples for plotting raster and vector data
- examples for reprojection, resampling (using rasterio/gdal)
- sampling points from vector datasets
- custom (non-stationary) GP kernels for DSM
- algorithms for experimental design (DOE)
- 3D terrain survey
- ...?


Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
