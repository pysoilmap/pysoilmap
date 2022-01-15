# Configuration file for the Sphinx documentation builder.
# For more information, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
from glob import glob

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
    'folium': ('http://python-visualization.github.io/folium/', None),
    'geopandas': ('https://geopandas.org', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'python': ('https://docs.python.org/3', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference', None),
    'shapely': ('https://shapely.readthedocs.io/en/latest/', None),
    'xarray': ('http://xarray.pydata.org/en/stable', None),
}


# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_theme_options = {'page_width': '970px'}
html_static_path = ['_static']
html_css_files = ['custom.css']

nbsphinx_prompt_width = '0px'
nbsphinx_execute = 'never'


# -- Build or download the example notebooks ---------------------------------

rtds_action_github_token = os.environ.get('RTD_GITHUB_TOKEN')
if rtds_action_github_token:
    rtds_action_path = 'examples'
    rtds_action_github_repo = 'pysoilmap/pysoilmap'
    rtds_action_artifact_prefix = 'notebooks-for-'
    rtds_action_error_if_missing = False
    extensions.append('rtds_action')
else:
    def setup(app):
        import jupytext
        for filename in glob('examples/*.py'):
            basename, ext = os.path.splitext(filename)
            src = basename + '.py'
            dst = basename + '.ipynb'
            modify_window = 1.0
            if os.path.getmtime(src) > os.path.getmtime(dst) + modify_window:
                print("Converting to notebook:", src)
                nb = jupytext.read(src)
                jupytext.write(nb, dst)
