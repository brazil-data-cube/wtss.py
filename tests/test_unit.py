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
import requests

from wtss.wtss import WTSS


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


class TestServiceInfo:
    """Regression tests for B2: requests.exceptions.HTTPError handling.

    ``_service_info`` used to catch ``urllib.error.HTTPError``, which is never
    raised by ``requests``. A 4xx/5xx response leaked the requests HTTPError
    untouched instead of becoming a friendly ``RuntimeError``.
    """

    def test_http_error_becomes_runtime_error(self, monkeypatch):
        """A requests HTTPError from the root request must become RuntimeError."""
        def raise_http_error(*args, **kwargs):
            raise requests.exceptions.HTTPError('500 Server Error')

        monkeypatch.setattr(WTSS, '_request', staticmethod(raise_http_error))

        with pytest.raises(RuntimeError, match='Not a valid Web Time Series Service'):
            WTSS('http://example.com/wtss')

    def test_missing_key_becomes_runtime_error(self, monkeypatch):
        """A malformed root response (missing keys) must become RuntimeError."""
        monkeypatch.setattr(WTSS, '_request', staticmethod(lambda *a, **k: {}))

        with pytest.raises(RuntimeError, match='Not a valid Web Time Series Service'):
            WTSS('http://example.com/wtss')
