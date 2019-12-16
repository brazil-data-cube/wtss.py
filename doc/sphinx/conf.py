#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2019 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Configuration file for the Sphinx documentation builder system."""
import os


# -- Project information -----------------------------------------------------

project = 'wtss'
copyright = '2019, INPE'
author = 'INPE'

g = {}

with open(os.path.join('..', '..', 'wtss', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

# The full version, including alpha/beta/rc tags.
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

def setup(app):
    app.add_stylesheet('wtss.css')

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

todo_emit_warnings = True

master_doc = 'index'