import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def add_colorbar(obj=None, size: float = 0.15, pad: float = 0.1, **kw):
    """Add colorbar to axes with the same height as the axes.

    :param obj: a :class:`matplotlib.cm.ScalarMappable` or an
                :class:`matplotlib.axes.Axes` instance
    :param size: colorbar size (width)
    :param pad: padding between axes and colorbar
    :param kw: keyword arguments for :meth:`Figure.colorbar`
    """
    if obj is None:
        obj = plt.gca()
    if isinstance(obj, mpl.cm.ScalarMappable):
        ax = obj.axes
        im = obj
    elif isinstance(obj, mpl.axes.Axes):
        ax = obj
        im = next(
            child for child in obj.get_children()
            if isinstance(child, mpl.cm.ScalarMappable))
    else:
        raise TypeError(
            "Expected a `matplotlib.axes.Axes` or a `mpl.cm.ScalarMappable` "
            "as first argument. Got: {!r}".format(obj))
    fig = ax.figure
    try:
        divider = ax.colorbar_divider
        pad = 1.0
    except AttributeError:
        divider = ax.colorbar_divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=size, pad=pad)
    cbar = fig.colorbar(im, cax=cax, **kw)
    return cbar
