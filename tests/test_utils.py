#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
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

"""Unit-test for WTSS utility functions."""

from wtss.utils import render_html


def test_render_html_loads_package_template():
    """Verify packaged templates load without pkg_resources."""
    rendered = render_html('wtss.html',
                           url='https://example.test/wtss',
                           coverages=['MOD13Q1'])

    assert 'https://example.test/wtss' in rendered
    assert 'MOD13Q1' in rendered
