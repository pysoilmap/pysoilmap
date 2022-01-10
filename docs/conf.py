# Configuration file for the Sphinx documentation builder.
# For more information, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pysoilmap

import inspect
import sphinx_autodoc_typehints

# -- Project information -----------------------------------------------------

project = 'pysoilmap'
copyright = '2021, Thomas Gläßle'
author = 'Thomas Gläßle'
release = pysoilmap.__version__


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_automodapi.automodapi',
    'sphinx_automodapi.smart_resolver',     # see sphinx-autodoc-typehints#38
    'sphinx_autodoc_typehints',
    'sphinx_click',
    'nbsphinx',
]

add_module_names = False
automodapi_toctreedirnm = "automod"
automodapi_writereprocessed = False
automodsumm_inherited_members = True
typehints_fully_qualified = False
typehints_document_rtype = True

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'geopandas': ('https://geopandas.org', None),
    'shapely': ('https://shapely.readthedocs.io/en/latest/', None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "matplotlib": ("https://matplotlib.org/", None),
    'xarray': ('http://xarray.pydata.org/en/stable', None),
}


# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'


# -- Fix broken intersphinx links to Polygon ---------------------------------
# See: https://github.com/agronholm/sphinx-autodoc-typehints/issues/38
qualname_overrides = {
    'shapely.geometry.polygon.Polygon': 'Polygon',
}


def format_annotation(annotation, *args, **kwargs):
    if inspect.isclass(annotation):
        full_name = f'{annotation.__module__}.{annotation.__qualname__}'
        override = qualname_overrides.get(full_name)
        if override is not None:
            return f':py:class:`~{override}`'
    return format_annotation_original(annotation, *args, **kwargs)


format_annotation_original = sphinx_autodoc_typehints.format_annotation
sphinx_autodoc_typehints.format_annotation = format_annotation


def setup(app):
    import os
    import jupytext
    for fname in os.listdir('examples'):
        if fname.endswith('.py'):
            print("Converting to notebook:", fname)
            base, ext = os.path.splitext(fname)
            nb = jupytext.read(os.path.join('examples', fname))
            jupytext.write(nb, os.path.join('examples', base + '.ipynb'))
