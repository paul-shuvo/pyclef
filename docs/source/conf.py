# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyclef'
copyright = '2026, Shuvo Paul'
author = 'Shuvo Paul'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',    # Automatically generate documentation from docstrings
    'sphinx.ext.napoleon',   # Support for Google/NumPy-style docstrings
    'sphinx.ext.viewcode',   # Add links to source code
]

templates_path = ['_templates']
exclude_patterns = []

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'shibuya'
html_static_path = ['_static']
