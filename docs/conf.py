# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import datetime

author = 'spon'
email = 'lisponsored@gmail.com'
project = '纸上谈兵'
copyright = f'{datetime.datetime.today().year}, {email}'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# search contrib from https://github.com/topics/sphinx-extension
extensions = [
    'sphinx.ext.todo',
    'sphinx_rtd_theme',
    'sphinx_copybutton',
    'sphinx_multiversion',
    'sphinxcontrib.mermaid',
    'sphinxcontrib.youtube',
    'sphinxcontrib.video',
]

templates_path = ['_templates']
exclude_patterns = []

# language = 'zh_CN'
language = 'en'

todo_include_todos = True

# || Options for HTML output -------------------------------------------------
# vv
#    https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
custom_rtd = True
if html_theme == 'sphinx_rtd_theme' and custom_rtd:
    # see: https://stackoverflow.com/a/62338678
    html_style = 'css/custom_theme.css'
    # see: https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
    html_theme_options = {
        'analytics_id': 'G-XXXXXXXXXX',  # Provided by Google in your dashboard
        'analytics_anonymize_ip': False
    }

html_context = {
    'display_github': True
}

html_static_path = ['_static']

# ^^
# || END Options for HTML output ---------------------------------------------


# || Mermaid configuration
# vv
# see: https://github.com/mgaitan/sphinxcontrib-mermaid/blob/master/sphinxcontrib/mermaid.py#L427
mermaid_version = 'latest'
mermaid_d3_zoom = True
# ^^
# || END Mermaid configuration
