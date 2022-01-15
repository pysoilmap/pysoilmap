"""
Computation of topographic variables from a DEM.

The DEM's axes ordering is assumed to be ``(Y, X)`` in accordance with the
same convention as for :func:`numpy.meshgrid` or
:func:`matplotlib.pyplot.imshow`.
"""

import affine
import numpy as np
import pyproj
import scipy.ndimage as ndimage
import scipy.misc as misc

import functools
import inspect
import numbers


def _cachedmethod(func: callable) -> callable:
    """Simple decorator for creating methods that cache results based on their
    hashable, positional arguments. Expects that ``self._cache`` is a dict."""
    @functools.wraps(func)
    def wrapper(self, *args):
        cache = self._cache.setdefault(func, {})
        try:
            value = cache[args]
        except KeyError:
            value = cache[args] = func(self, *args)
        return value
    wrapper.__signature__ = inspect.signature(func)
    return wrapper


def diff_finite(
    dem: np.ndarray,
    cellsize: tuple,
    dx: int,
    dy: int,
) -> np.ndarray:
    """
    Calculate a higher-order derivative of the DEM by finite differencing
    successively in X and then Y direction. Uses a central differencing scheme.

    :param dem: DEM (z values at each pixel of a rectangular grid)
    :param cellsize: pixel ``(width, height)``
    :param dx: order of derivative in x direction
    :param dy: order of derivative in y direction
    """
    wx = misc.central_diff_weights(dx + 1 + dx % 2, dx).reshape(1, -1)
    wy = misc.central_diff_weights(dy + 1 + dy % 2, dy).reshape(-1, 1)
    image = _as_float_array(dem)
    image = ndimage.convolve(image, wx, mode='nearest')
    image = ndimage.convolve(image, wy, mode='nearest')
    norm = np.product(cellsize ** np.array([dy, dx]))
    return image / norm


def diff_gauss(
    dem: np.ndarray,
    cellsize: tuple,
    dx: int,
    dy: int,
    sigma: float = 1,
) -> np.ndarray:
    """
    Applies a Gaussian derivative filter to the given DEM.

    This is the same as smoothing the DEM with the given lengthscale ``sigma``
    and then calculating the nth-order derivatives in the given directions.

    :param dem: DEM (z coordinates of each pixel of a regular rectangular grid)
    :param cellsize: pixel ``(width, height)``
    :param dx: order of derivative in x direction
    :param dy: order of derivative in y direction
    :param sigma: lengthscale in unit of pixels
    """
    norm = np.product(cellsize ** np.array([dy, dx]))
    image = _as_float_array(dem)
    image = ndimage.gaussian_filter(image, order=[dy, dx], sigma=sigma)
    return image / norm


class Topography:

    """
    Calculates various topographic indices at each pixel from on a given DEM.

    :param dem: DEM, i.e. z coordinates of each pixel
    :param cellsize: Size of a pixel given as pair ``(width, height)``
    :param diff: differentiation function. Either :func:`diff_finite`,
                 or :func:`diff_gauss`
    :param indexing: either ``xy`` or ``ij``, same meaning as for
                     ``numpy.meshgrid``
    :param transform: list of 6 numbers that describe the transformation.
                      Only used for ``latitude``, ``rad_angle``, and
                      ``sun_exposure``.
    :param crs: Name of the coordinate system. Only used for ``latitude``,
                ``rad_angle``, and ``sun_exposure``.
    :param kwargs: keyword arguments for ``diff``. Usually ``sigma=VALUE`` for
                   the gaussian derivative

    Note that the DEM is assumed to live on a regular rectangular grid.

    Note that the object caches some of the calculated quantities for reuse.
    In order to free memory you should let go of the ``Topography`` instance
    after calculation of the quantities in which you are interested
    """

    def __init__(
        self,
        dem: np.ndarray,
        cellsize: tuple,
        diff: callable = diff_finite,
        indexing: str = 'xy',
        transform: list = None,
        crs: str = None,
        **kwargs,
    ):
        self._cache = {}
        self._dem = _as_float_array(dem)
        self._diff = diff
        self._transform = transform
        self._crs = crs
        self._kwargs = kwargs
        if isinstance(cellsize, numbers.Number):
            self._cellsize = (cellsize, cellsize)
        elif isinstance(cellsize, (tuple, list)):
            self._cellsize = cellsize
        else:
            raise TypeError(
                "Expected a number for `cellsize`, but received a {!r}: {!r}"
                .format(type(cellsize), cellsize))
        self._indexing = ''.join(indexing)
        if self._indexing not in ('xy', 'ij'):
            raise ValueError("Invalid indexing: {!r}".format(self._indexing))
        self._transform = transform and affine.Affine(*transform)

    @_cachedmethod
    def diff(self, dx: int, dy: int) -> np.ndarray:
        """Differentiate the DEM ``dx`` times in X direction and ``dy`` times
        in Y direction."""
        if self._indexing == 'ij':
            dx, dy = dy, dx
        return self._diff(self._dem, self._cellsize, dx, dy, **self._kwargs)

    def D1x(self) -> np.ndarray:
        """Calculate the first derivative (slope) of the DEM in X direction.
        Same as ``self.diff(1, 0)``."""
        return self.diff(1, 0)

    def D1y(self) -> np.ndarray:
        """Calculate the first derivative (slope) of the DEM in Y direction.
        Same as ``self.diff(0, 1)``."""
        return self.diff(0, 1)

    def D2x(self) -> np.ndarray:
        """Calculate the 2nd derivative (curvature) of the DEM in X direction.
        Same as ``self.diff(2, 0)``."""
        return self.diff(2, 0)

    def D2y(self) -> np.ndarray:
        """Calculate the 2nd derivative (curvature) of the DEM in Y direction.
        Same as ``self.diff(0, 2)``."""
        return self.diff(0, 2)

    @_cachedmethod
    def _Dxy(self) -> np.ndarray:
        """Differentiate the DEM with respect to both X and Y, and then
        multiply by the individual derivatives.

        Same as ``self.diff(1, 1) * D1x * D1y``."""
        return self.diff(1, 1) * self.D1x() * self.D1y()

    @_cachedmethod
    def Dx2(self) -> np.ndarray:
        """Return the square of the X slope. Same as ``D1x**2``."""
        return self.D1x() ** 2

    @_cachedmethod
    def Dy2(self) -> np.ndarray:
        """Return the square of the Y slope. Same as ``D1y**2``."""
        return self.D1y() ** 2

    @_cachedmethod
    def _p(self) -> np.ndarray:
        """Returns the square of the total slope.
        Same as ``slope_x**2 + slope_y**2``."""
        return self.Dx2() + self.Dy2()

    @_cachedmethod
    def _q(self) -> np.ndarray:
        """Returns ``slope_x**2 + slope_y**2 + 1``."""
        return self._p() + 1

    @_cachedmethod
    def slope(self) -> np.ndarray:
        """Returns the absolute value of the total slope.
        Same as ``sqrt(D1x**2 + D1y**2)``."""
        return np.sqrt(self._p())

    slope_x = D1x
    slope_y = D1y

    def curvature(self) -> np.ndarray:
        """Returns the absolute value of the total curvature.
        Same as ``sqrt(D2x**2 + D2y**2)``."""
        return np.sqrt(self.D2x()**2 + self.D2y()**2)

    curvature_x = D2x
    curvature_y = D2y

    def plan_curvature(self) -> np.ndarray:
        """Calculate the planform curvature, i.e. the curvature of the terrain
        surface in the horizontal plane.

        See:
        - http://surferhelp.goldensoftware.com/gridops/plan_curvature.htm
        - Map Use: Reading, Analysis, Interpretation, Seventh Edition (p. 360)
        """
        return _safe_divide(
            self.D2x() * self.Dy2() +
            self.Dx2() * self.D2y() - 2 * self._Dxy(),
            self._p() ** 1.5,
            fill=0)

    def tang_curvature(self) -> np.ndarray:
        """Calculate the tangential curvature, i.e. the curvature of a terrain
        cross-section on a vertical plane perpendicular to the gradient
        direction.

        See:
        - http://surferhelp.goldensoftware.com/gridops/tangential_curvature.htm
        - Map Use: Reading, Analysis, Interpretation, Seventh Edition (p. 360)
        """
        return _safe_divide(
            self.D2x() * self.Dy2() +
            self.Dx2() * self.D2y() - 2 * self._Dxy(),
            self._q()**0.5 * self._p(),
            fill=0)

    def prof_curvature(self) -> np.ndarray:
        """Calculate the profile curvature., i.e. the curvature of a terrain
        cross-section on a vertical plane containing the gradient vector.

        See:
        - http://surferhelp.goldensoftware.com/gridops/profile_curvature.htm
        - Map Use: Reading, Analysis, Interpretation, Seventh Edition (p. 360)
        """
        return _safe_divide(
            self.D2x() * self.Dx2() +
            self.Dy2() * self.D2y() + 2 * self._Dxy(),
            self._q()**1.5 * self._p(),
            fill=0)

    def northness(self) -> np.ndarray:
        """Calculate the northness, i.e. the cosine-transformed aspect.

        This quantity can be understood as the projected length of the gradient
        direction on the north axis in the horizontal plane."""
        return np.sin(self.grad_dir())

    def eastness(self) -> np.ndarray:
        """Calculate the eastness, i.e. the sine-transformed aspect.

        This quantity can be understood as the projected length of the gradient
        direction on the east axis in the horizontal plane."""
        return -np.cos(self.grad_dir())

    @_cachedmethod
    def aspect(self) -> np.ndarray:
        """Returns the angle of the gradient direction in radians counted from
        north in clockwise direction."""
        return 3 * np.pi / 2 - self.grad_dir()

    @_cachedmethod
    def grad_dir(self) -> np.ndarray:
        """Returns the angle of the gradient direction in radians counted from
        east in counter-clockwise direction (i.e. mathematical convention)."""
        return np.arctan2(self.D1y(), self.D1x())

    @_cachedmethod
    def slope_angle(self) -> np.ndarray:
        """Returns the slope angle, i.e. the angle between the horizontal
        plane and the gradient vector. This is a non-negative value."""
        return np.arctan(self.slope())

    @_cachedmethod
    def slope_angle_x(self) -> np.ndarray:
        """Returns the x slope angle, i.e. the angle between the x axis
        and the surface in the xz plane."""
        return np.arctan(self.slope_x())

    @_cachedmethod
    def slope_angle_y(self) -> np.ndarray:
        """Returns the y slope angle, i.e. the angle between the y axis
        and the surface in the yz plane."""
        return np.arctan(self.slope_y())

    def verticality(self) -> np.ndarray:
        """Sine of the slope angle."""
        return np.sin(self.slope_angle())

    def verticality_x(self) -> np.ndarray:
        """Sine of the x slope angle."""
        return np.sin(self.slope_angle_x())

    def verticality_y(self) -> np.ndarray:
        """Sine of the y slope angle."""
        return np.sin(self.slope_angle_y())

    @_cachedmethod
    def latitude(self) -> np.ndarray:
        """Get the latitude in radians at each pixel."""
        if self._crs is None or self._transform is None:
            raise ValueError(
                "In order to use this method the `crs` and `transform` "
                "parameters must be defined when initializing the "
                "Topography() object!")
        if self._indexing == 'xy':
            ny, nx = self._dem.shape
        else:
            nx, ny = self._dem.shape
        xs, ys = self._transform * np.meshgrid(
            np.linspace(0, nx - 1, nx),
            np.linspace(0, ny - 1, ny),
            indexing=self._indexing)
        return get_latitude(xs, ys, self._crs)

    def sun_exposure(self, declination=0) -> np.ndarray:
        """
        Return the cosine of the angle between surface normal and the sun at
        midday.

        :param declination: sun declination angle in radians. Can be used to
                            adjust for season. A positive value corresponds to
                            a northward deviation. Zero means the sun is in the
                            zenith over the equator.

        This is very similar to ``rad_angle`` but not exactly the same.
        """
        return sun_exposure(
            self.grad_dir(),
            self.slope(),
            self.latitude(),
            declination)

    def rad_angle(self, declination=0) -> np.ndarray:
        """
        Return the cosine of the "radiation angle" according to Herbsta, et al
        2006 [1].

        :param declination: sun declination angle in radians. Can be used to
                            adjust for seasonal changes.

        All input arguments must be of the same shape or scalars.

        The formulate is taken from Herbsta, et al. 2006 [1] who cite Moore, et
        al. 1988 [2] as source - which doesn't mention the formula anywhere.

        [1] (2006 Geostatistical co-regionalization of soil hydraulic
        properties in a microscale catchment using terrain attributes
        [Herbsta, et al.])

        [2] Moore, I.D., Burch, G.J., Mackenzie, D.H., 1988. Topographic
        effects on the distribution of surface soil water and the location
        of ephemeral gullies. American Society of Agricultural Engi-
        neers 31 (4), 1098 – 1107.
        """
        return rad_angle(
            self.aspect(),
            self.slope(),
            self.latitude(),
            declination)


def get_latitude(
    xs: np.ndarray,
    ys: np.ndarray,
    crs: str,
):
    """Calculate the latitude for each pair of (X, Y) coordinates in
    the given CRS.

    :param xs: array of X coordinates
    :param ys: array of Y coordinates
    :param crs: name of the coordinate system
    """
    to_wgs84 = pyproj.Transformer.from_crs(crs, 'epsg:4326', always_xy=True)
    lon, lat = to_wgs84.transform(xs, ys)
    return lat * (np.pi / 180)


def sun_exposure(grad_dir, slope, latitude, declination=0.0):
    """
    Return the cosine of the angle between surface normal and the sun at
    midday.

    :param grad_dir: direction of the gradient in XY plane in radians
                     in counter-clockwise direction with respect to east
    :param slope: inclination of the gradient in radians
    :param latitude: point latitude in radians
    :param declination: sun declination angle in radians. Can be used to
                        adjust for season. A positive value corresponds to
                        a northward deviation. Zero means the sun is in the
                        zenith over the equator.

    All input arguments must be of the same shape or scalar.

    This is very similar to ``rad_angle`` but not exactly the same.
    """
    delta = latitude - declination
    sun_vector = np.array([
        np.zeros_like(delta),
        -np.sin(delta),
        np.cos(delta),
    ])
    plane_normal = np.array([
        -np.cos(grad_dir) * np.sin(slope),
        -np.sin(grad_dir) * np.sin(slope),
        np.cos(slope),
    ])
    return np.sum(sun_vector * plane_normal, axis=0)


def rad_angle(aspect, slope, latitude, declination=0.0):
    """
    Return the cosine of the "radiation angle" according to Herbsta, et al
    2006 [1].

    :param aspect: direction of the gradient in XY plane in radians in
                   clockwise direction with respect to north
    :param slope: inclination of the gradient in radians
    :param latitude: point latitude in radians
    :param declination: sun declination angle in radians

    All input arguments must be of the same shape or scalar.

    The formula is taken from Herbsta, et al. 2006 [1]. They cite Moore, et al.
    1988 [2] as source - which doesn't seem to mention the formula anywhere.

    [1] (2006 Geostatistical co-regionalization of soil hydraulic properties
    in a microscale catchment using terrain attributes [Herbsta, et al.])

    [2] Moore, I.D., Burch, G.J., Mackenzie, D.H., 1988. Topographic
     effects on the distribution of surface soil water and the location
     of ephemeral gullies. American Society of Agricultural Engi-
     neers 31 (4), 1098 – 1107.
    """
    delta = latitude - declination
    b = 1 + np.sin(slope)**2 * np.cos(aspect)**2
    c = 2 * np.sin(slope) * np.cos(slope) * np.cos(aspect) * np.sin(delta)
    d = np.cos(slope)**2 * np.sin(delta) - 1
    return (-c + np.sqrt(c**2 - 4 * b * d)) / (2*b)


def _as_float_array(array: np.ndarray, min_float=np.float32) -> np.ndarray:
    """Convert array to a floating point array."""
    array = np.asanyarray(array)
    dtype = np.result_type(array, min_float)
    return np.asanyarray(array, dtype=dtype)


def _safe_divide(a: np.ndarray, b: np.ndarray, fill=np.nan) -> np.ndarray:
    """Perform division without complaining about division by zero. Fills
    nan/inf values by the given fill value (can be an array that broadcasts
    to the result shape)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.divide(a, b)
        result = np.where(np.isfinite(result), result, fill)
        return result
