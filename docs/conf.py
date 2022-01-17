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
    'sphinx_automodapi.smart_resolver',
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

templates_path = ['_templates']
html_css_files = ['custom.css']
html_static_path = ['_static']
html_context = {
    'repo_url': 'https://github.com/pysoilmap/pysoilmap',
    'source_url': 'https://github.com/pysoilmap/pysoilmap/blob/main',
    'display_github': True,
}

# https://alabaster.readthedocs.io/en/latest/customization.html
html_theme = 'alabaster'
html_theme_options = {}

# https://nbsphinx.readthedocs.io/en/0.8.2/usage.html
nbsphinx_prompt_width = '0px'
nbsphinx_execute = 'never'


# -- Build or download the example notebooks ---------------------------------

rtds_action_github_token = os.environ.get('RTD_GITHUB_TOKEN')
rtds_action_path = 'examples'
rtds_action_github_repo = 'pysoilmap/pysoilmap'
rtds_action_artifact_prefix = 'notebooks-for-'
rtds_action_error_if_missing = False


def setup(app):
    app.connect("html-page-context", html_page_context)
    if rtds_action_github_token:
        app.setup_extension('rtds_action')
    else:
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


def html_page_context(app, pagename, templatename, context, doctree):
    """Avoid broken source links to auto-generated API-docs."""
    pagesuffix = context.get('page_source_suffix')
    if pagesuffix == '.ipynb':
        pagesuffix = '.py'
    if pagename.startswith('automod/'):
        modname = pagename.split('/', 1)[1].rsplit('.', 1)[0]
        srcname = 'src/{}.py'.format(modname.replace('.', '/'))
    elif pagename.startswith('_modules/'):
        modname = pagename.split('/', 1)[1]
        srcname = 'src/{}.py'.format(modname.replace('.', '/'))
    elif context['hasdoc'](pagename):
        srcname = 'docs/{}{}'.format(pagename, pagesuffix)
    else:
        srcname = None
    context['page_source'] = srcname
