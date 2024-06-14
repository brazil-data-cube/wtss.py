#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2024 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

"""Utility functions for WTSS client library."""

import jinja2
from pkg_resources import resource_filename

_template_loader = jinja2.FileSystemLoader(searchpath=resource_filename(__name__, 'templates/'))

_template_env = jinja2.Environment(loader=_template_loader,
                                   autoescape=jinja2.select_autoescape(['html']))


def render_html(template_name, **kwargs):
    """Render Jinja2 HTML template."""
    template = _template_env.get_template(template_name)
    return template.render(**kwargs)