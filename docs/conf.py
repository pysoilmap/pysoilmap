# Configuration file for the Sphinx documentation builder.
# For more information, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pysoilmap

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


def setup(app):
    import os
    import jupytext
    for fname in os.listdir('examples'):
        if fname.endswith('.py'):
            print("Converting to notebook:", fname)
            base, ext = os.path.splitext(fname)
            nb = jupytext.read(os.path.join('examples', fname))
            jupytext.write(nb, os.path.join('examples', base + '.ipynb'))
