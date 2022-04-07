#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Utility functions for WTSS client library."""

from datetime import datetime

import jinja2
from pkg_resources import resource_filename

_template_loader = jinja2.FileSystemLoader(searchpath=resource_filename(__name__, 'templates/'))

_template_env = jinja2.Environment(loader=_template_loader,
                                   autoescape=jinja2.select_autoescape(['html']))


def render_html(template_name, **kwargs):
    """Render Jinja2 HTML template."""
    template = _template_env.get_template(template_name)
    return template.render(**kwargs)