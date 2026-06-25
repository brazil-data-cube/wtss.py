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

import inspect

import numpy
import pytest
import requests
import urllib3
from requests.adapters import HTTPAdapter

from wtss.coverage import Coverage
from wtss.wtss import WTSS

#: Minimal valid service root used to build a WTSS client without a server.
_ROOT = {'wtss_version': '2.0', 'links': []}


def _stub_request(monkeypatch, root=None):
    """Make ``WTSS._request`` return a canned root so ``__init__`` succeeds offline."""
    monkeypatch.setattr(WTSS, '_request', staticmethod(lambda *a, **k: root or _ROOT))


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

    Note: since B4 the metadata is fetched lazily, so the error surfaces on the
    first metadata access (``.coverages``), not in the constructor.
    """

    def test_http_error_becomes_runtime_error(self, monkeypatch):
        """A requests HTTPError from the root request must become RuntimeError."""
        def raise_http_error(*args, **kwargs):
            raise requests.exceptions.HTTPError('500 Server Error')

        monkeypatch.setattr(WTSS, '_request', staticmethod(raise_http_error))

        service = WTSS('http://example.com/wtss')
        with pytest.raises(RuntimeError, match='Not a valid Web Time Series Service'):
            service.coverages

    def test_missing_key_becomes_runtime_error(self, monkeypatch):
        """A malformed root response (missing keys) must become RuntimeError."""
        monkeypatch.setattr(WTSS, '_request', staticmethod(lambda *a, **k: {}))

        service = WTSS('http://example.com/wtss')
        with pytest.raises(RuntimeError, match='Not a valid Web Time Series Service'):
            service.coverages


class TestLazyServiceInfo:
    """Regression tests for B4: ``__init__`` must not perform any HTTP.

    The service root used to be fetched eagerly in the constructor, coupling
    instantiation to network state. It is now fetched on first metadata use.
    """

    def test_construct_makes_no_request(self, monkeypatch):
        calls = []
        monkeypatch.setattr(
            WTSS, '_request',
            staticmethod(lambda *a, **k: (calls.append(k.get('op')), _ROOT)[1]),
        )
        service = WTSS('http://example.com/wtss')
        assert calls == []  # B4: nothing fetched yet

        _ = service.coverages  # first metadata access triggers the fetch
        assert calls == ['/']

    def test_version_triggers_fetch(self, monkeypatch):
        _stub_request(monkeypatch, {'wtss_version': '2.0', 'links': []})
        service = WTSS('http://example.com/wtss')
        assert service._version is None  # not fetched on construction
        assert service.version == '2.0'  # property fetches lazily


class _FakeResponse:
    """Minimal stand-in for a requests.Response."""

    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


class TestHttpSession:
    """Regression tests for F3: a pooled Session with timeout and retries.

    Each request used to open a fresh connection with no timeout and no retry.
    The client now reuses a ``requests.Session`` with a retry/backoff adapter
    and forwards a per-request timeout.
    """

    def test_session_is_created(self):
        assert isinstance(WTSS('http://example.com/wtss')._session, requests.Session)

    def test_retry_adapter_defaults(self):
        service = WTSS('http://example.com/wtss')
        retry = service._session.get_adapter('https://example.com/wtss').max_retries
        assert retry.total == 3
        assert retry.backoff_factor == 0.5
        assert {502, 503, 504} <= set(retry.status_forcelist)

    def test_both_schemes_use_retry_adapter(self):
        service = WTSS('http://example.com/wtss')
        for scheme in ('http://x', 'https://x'):
            assert isinstance(service._session.get_adapter(scheme), HTTPAdapter)

    def test_retries_and_timeout_are_configurable(self):
        service = WTSS('http://example.com/wtss', retries=5, timeout=7)
        assert service._timeout == 7
        assert service._session.get_adapter('https://x').max_retries.total == 5

    def test_request_forwards_timeout_and_verify(self, monkeypatch):
        service = WTSS('http://example.com/wtss', timeout=12)
        captured = {}

        def fake_request(method, url, **kwargs):
            captured.update(kwargs)
            return _FakeResponse({'wtss_version': '2.0', 'links': []})

        monkeypatch.setattr(service._session, 'request', fake_request)
        _ = service.coverages  # triggers the lazy service-info request

        assert captured['timeout'] == 12
        assert captured['verify'] is True


class TestCliTs:
    """Regression tests for B3: the ``wtss ts`` command options.

    Click declared ``--start-date``/``--end-date`` (kwargs ``start_date`` /
    ``end_date``), but the callback expects ``start_datetime`` /
    ``end_datetime``, so any invocation raised ``TypeError`` on binding.
    """

    def test_option_names_match_callback_signature(self):
        """Every Click option must map to a parameter the callback accepts."""
        from wtss.cli import ts

        callback_params = set(inspect.signature(ts.callback).parameters)
        click_params = {p.name for p in ts.params}

        unexpected = click_params - callback_params
        assert not unexpected, f'options not accepted by callback: {unexpected}'

    def test_datetime_options_present(self):
        """The renamed datetime options must exist."""
        from wtss.cli import ts

        click_params = {p.name for p in ts.params}
        assert {'start_datetime', 'end_datetime'} <= click_params


class TestGetattrPrivateNames:
    """Regression tests for B6: ``__getattr__`` must reject private/dunder names.

    Probes such as ``__reduce_ex__`` or ``_ipython_*`` used to fall through to a
    coverage lookup (and could recurse through ``coverages`` before it was ready).
    """

    def test_private_attr_raises_without_coverage_lookup(self, monkeypatch):
        _stub_request(monkeypatch, {'wtss_version': '2.0',
                                    'links': [{'rel': 'data', 'title': 'X MOD13Q1-6'}]})
        service = WTSS('http://example.com/wtss')
        # Coverage cache starts empty and must stay empty after a private probe.
        assert service._collections == []
        with pytest.raises(AttributeError):
            service._not_a_real_attribute
        assert service._collections == []

    def test_dunder_probe_does_not_raise_keyerror(self, monkeypatch):
        _stub_request(monkeypatch)
        service = WTSS('http://example.com/wtss')
        # hasattr swallows AttributeError; the point is it does not blow up.
        assert hasattr(service, '__wrapped__') is False


class TestLatLonValidation:
    """Regression tests for B13: numeric latitude/longitude type checking.

    ``type(x) not in (float, int)`` rejected ``numpy.float64`` and friends; the
    check now uses ``numbers.Real`` (while still rejecting ``bool``).
    """

    def test_accepts_numpy_float(self):
        opts = Coverage._check_input_parameters(
            attributes=['NDVI'],
            latitude=numpy.float64(-12.0),
            longitude=numpy.float64(-54.0),
        )
        assert opts['geom']['type'] == 'Point'
        assert [float(c) for c in opts['geom']['coordinates']] == [-54.0, -12.0]

    def test_accepts_numpy_int(self):
        opts = Coverage._check_input_parameters(
            attributes=['NDVI'],
            latitude=numpy.int32(-12),
            longitude=numpy.int32(-54),
        )
        assert opts['geom']['type'] == 'Point'

    def test_accepts_plain_python_numbers(self):
        opts = Coverage._check_input_parameters(attributes=['NDVI'], latitude=-12, longitude=-54.0)
        assert opts['geom']['type'] == 'Point'

    def test_rejects_bool(self):
        with pytest.raises(ValueError, match='must be numeric'):
            Coverage._check_input_parameters(attributes=['NDVI'], latitude=True, longitude=-54.0)

    def test_rejects_string(self):
        with pytest.raises(ValueError, match='must be numeric'):
            Coverage._check_input_parameters(attributes=['NDVI'], latitude='-12', longitude=-54.0)


class TestSslVerification:
    """Regression tests for B19/B20: SSL verification and warning suppression.

    B20: the ``REQUEST_SSL_VERIFY`` flag is read once in ``__init__`` instead of
    on every request. B19: ``urllib3.disable_warnings`` is opt-in, not a global
    side effect of each call.
    """

    def test_verify_ssl_defaults_true(self, monkeypatch):
        monkeypatch.delenv('REQUEST_SSL_VERIFY', raising=False)
        _stub_request(monkeypatch)
        assert WTSS('http://example.com/wtss')._verify_ssl is True

    def test_verify_ssl_read_from_env(self, monkeypatch):
        monkeypatch.setenv('REQUEST_SSL_VERIFY', '0')
        _stub_request(monkeypatch)
        assert WTSS('http://example.com/wtss')._verify_ssl is False

    def test_explicit_arg_overrides_env(self, monkeypatch):
        monkeypatch.setenv('REQUEST_SSL_VERIFY', '1')
        _stub_request(monkeypatch)
        assert WTSS('http://example.com/wtss', verify_ssl=False)._verify_ssl is False

    def test_warnings_not_disabled_by_default(self, monkeypatch):
        calls = []
        monkeypatch.setattr(urllib3, 'disable_warnings', lambda *a, **k: calls.append(1))
        _stub_request(monkeypatch)
        # Insecure connection but no opt-in => global urllib3 state untouched.
        WTSS('http://example.com/wtss', verify_ssl=False)
        assert calls == []

    def test_warnings_disabled_once_when_opted_in(self, monkeypatch):
        calls = []
        monkeypatch.setattr(urllib3, 'disable_warnings', lambda *a, **k: calls.append(1))
        _stub_request(monkeypatch)
        WTSS('http://example.com/wtss', verify_ssl=False, disable_ssl_warnings=True)
        assert len(calls) == 1
