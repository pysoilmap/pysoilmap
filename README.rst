pysoilmap
=========

|Version| |License|

Tools for performing Digital Soil Mapping (DSM) with python.

This project aims to provide a high-level user interface and examples for
common tasks related to DSM, accessible through a command line interface or
python APIs. The actual legwork is done by established libraries for numerical
computations, machine-learning, image-processing, geostatistics, projections,
geometries, file-formats, etc. Customized solutions are implemented where
needed or more convenient.

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
- sampling points from shapefile datasets
- custom non-stationary GP kernels for DSM
- algorithms for experimental design (DOE)
- 3D terrain survey
- ...?


Links
~~~~~

- Documentation (TBD)
- Tests (TBD)
- `Source Code`_
- License_

.. _Source Code: https://github.com/pysoilmap/pysoilmap
.. _License: https://github.com/pysoilmap/pysoilmap/blob/master/UNLICENSE


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
   :alt:                Version

.. |License| image::    https://img.shields.io/pypi/l/pysoilmap.svg
   :target:             https://github.com/pysoilmap/pysoilmap/blob/master/UNLICENSE
   :alt:                License: Unlicense
