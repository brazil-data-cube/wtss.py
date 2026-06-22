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

"""Unit tests that do not require a live WTSS server."""

import pytest


class TestStrtobool:
    """Regression tests for B1: inline ``strtobool`` replacing ``distutils``.

    ``distutils`` was removed in Python 3.12 (PEP 632); importing ``wtss.wtss``
    must not depend on it.
    """

    def test_no_distutils_import(self):
        """Importing the module must not pull in distutils."""
        import wtss.wtss  # noqa: F401 — import must succeed without distutils

    @pytest.mark.parametrize('value', ['y', 'Yes', 'T', 'true', 'ON', '1'])
    def test_true_values(self, value):
        from wtss.wtss import strtobool
        assert strtobool(value) == 1

    @pytest.mark.parametrize('value', ['n', 'No', 'F', 'false', 'OFF', '0'])
    def test_false_values(self, value):
        from wtss.wtss import strtobool
        assert strtobool(value) == 0

    @pytest.mark.parametrize('value', ['', 'maybe', '2', 'tru'])
    def test_invalid_values_raise(self, value):
        from wtss.wtss import strtobool
        with pytest.raises(ValueError):
            strtobool(value)
