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

"""Python Client Library for WTSS.

This module introduces a class named ``wtss`` that can be used to retrieve
satellite image time series for a given location.
"""
import os
from urllib.parse import urljoin

import requests
from requests.exceptions import HTTPError
import urllib3

from .coverage import Coverage
from .utils import render_html

#: Truthy/falsy string values accepted by :func:`strtobool`.
_TRUE_VALUES = {'y', 'yes', 't', 'true', 'on', '1'}
_FALSE_VALUES = {'n', 'no', 'f', 'false', 'off', '0'}


def strtobool(value: str) -> int:
    """Convert a string representation of truth to ``1`` (true) or ``0`` (false).

    Inline replacement for ``distutils.util.strtobool``, which was removed in
    Python 3.12 (PEP 632). Accepts the same values: true is ``y``, ``yes``,
    ``t``, ``true``, ``on`` and ``1``; false is ``n``, ``no``, ``f``, ``false``,
    ``off`` and ``0``. Comparison is case-insensitive.

    Raises:
        ValueError: If ``value`` is not a recognized truth value.
    """
    normalized = str(value).strip().lower()
    if normalized in _TRUE_VALUES:
        return 1
    if normalized in _FALSE_VALUES:
        return 0
    raise ValueError(f'invalid truth value {value!r}')


class WTSS:
    """Implement a client for WTSS.

    .. note::

        For more information about coverage definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self,
                 url: str,
                 validate = False,
                 access_token: str = None,
                 verify_ssl: bool = None,
                 disable_ssl_warnings: bool = False):
        """Create a WTSS client attached to the given host address (an URL).

        Args:
            url (str): URL for the WTSS server.
            validate (bool, optional): If True the client will validate the server response.
            access_token (str, optional): Authentication token to be used with the WTSS server.
            verify_ssl (bool, optional): Whether to verify the server TLS certificate.
                When ``None`` (default), it is read once from the ``REQUEST_SSL_VERIFY``
                environment variable (defaults to enabled).
            disable_ssl_warnings (bool, optional): Opt-in suppression of urllib3
                ``InsecureRequestWarning``. Only takes effect when ``verify_ssl`` is
                False. Defaults to False so the client never mutates global urllib3
                state behind the user's back.
        """
        #: str: URL for the WTSS server.
        self._url = url

        #: bool: If True the client will validate the server response.
        self._validate = validate

        #: str: Authentication token to be used with the WTSS server.
        self._access_token = access_token

        self._version = None

        self.parameters = dict(access_token=access_token)

        #: list: Service links; ``None`` until the metadata is fetched lazily (B4).
        self._links = None
        self._collections = []

        #: bool: TLS verification flag, read once instead of on every request (B20).
        if verify_ssl is None:
            verify_ssl = bool(strtobool(os.getenv('REQUEST_SSL_VERIFY', '1')))
        self._verify_ssl = verify_ssl

        # Suppress insecure-request warnings only when explicitly opted in,
        # instead of disabling them globally on every request (B19).
        if not self._verify_ssl and disable_ssl_warnings:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _service_info(self):
        try:
            root = self._request(self._url, method='get', op='/', params=self.parameters, verify=self._verify_ssl)
            self._version = root['wtss_version']
            self._links = root['links']
        except (KeyError, HTTPError) as e:
            raise RuntimeError('Not a valid Web Time Series Service.') from e

    def _ensure_service_info(self):
        """Fetch the service metadata on first use (B4: no HTTP in ``__init__``)."""
        if self._links is None:
            self._service_info()

    @property
    def version(self):
        """Return the WTSS server version, fetching service info on first use."""
        self._ensure_service_info()
        return self._version

    @property
    def coverages(self):
        """Return a list of coverage names.

        Returns:
            list: A list with the names of available coverages in the service.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        self._ensure_service_info()

        if len(self._collections) == 0:
            self._collections = [
                link['title'].rsplit(' ', 1)[-1]
                for link in self._links if link['rel'] == 'data'
            ]

        return self._collections

    def _retrieve_timeseries_or_summarize(self, coverage_name: str, route: str, params=None, **options):
        """Retrieve the time series for a given location.

        Keyword Args:
            coverage_name        (*required): Name of the coverage
            route                (*required): The desired operation ('timeseries' or 'summarize')
            attributes           (optional): A list containing the attributes names.
            geom                 (optional): The geometry to query
            latitude             (optional): A double that will be used with longitude if geom is not defined
            longitude            (optional): A double that will be used with latitude if geom is not defined
            start_datetime       (optional): A string representing the start datetime to query
            end_datetime         (optional): A string representing the end datetime to query
            applyAttributeScale: (optional): Boolean representing if results apply data scale for each attribute

        Returns:
            dict: A time series object as a dictionary.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        url = urljoin(self._url.strip('/') + '/', coverage_name)
        headers = {'x-api-key': self._access_token}
        request_result = WTSS._request(url,
                                       method='post',
                                       op=route,
                                       headers=headers,
                                       params=params,
                                       json=options,
                                       verify=self._verify_ssl)

        return request_result

    def __getitem__(self, key):
        """Get coverage whose name is identified by the key.

        Returns:
            Coverage: A coverage metadata object.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.

        Example:

            Get a coverage object named ``MOD13Q1``:

            .. doctest::
                :skipif: WTSS_EXAMPLE_URL is None

                >>> from wtss import *
                >>> service = WTSS(WTSS_EXAMPLE_URL)
                >>> service['MOD13Q1']
                Coverage...
        """
        if key not in self.coverages:
            raise KeyError(f'Coverage {key} not found.')

        # url = urljoin(self._url, key)
        coverage = self._request(self._url, op=key, method='get', params=self.parameters, verify=self._verify_ssl)

        return Coverage(service=self, metadata=coverage)

    def __getattr__(self, name: str):
        """Get coverage identified by name.

        Returns:
            Coverage: A coverage metadata object.

        Raises:
            AttributeError: If a coverage with the given name doesn't exist
                or could not be retrieved.

        Example:

            Get a coverage object named ``MOD13Q1``:

            .. doctest::
                :skipif: WTSS_EXAMPLE_URL is None

                >>> from wtss import *
                >>> service = WTSS(WTSS_EXAMPLE_URL)
                >>> service.MOD13Q1
                Coverage...
        """
        # Private/dunder names are never coverages. Reject them early so probes
        # like ``__reduce_ex__`` or ``_ipython_*`` do not trigger a coverage
        # lookup (and avoid recursing through ``coverages`` before it is set).
        if name.startswith('_'):
            raise AttributeError(f'No attribute named "{name}"')

        try:
            return self[name]
        except KeyError:
            raise AttributeError(f'No attribute named "{name}"')

    def __iter__(self):
        """Iterate over coverages available in the service.

        Returns:
            A coverage at each iteration.
        """
        for cv_name in self.coverages:
            yield self[cv_name]

    def __str__(self):
        """Return the string representation of the WTSS object."""
        text = f'WTSS:\n\tURL: {self._url}'

        return text

    def __repr__(self):
        """Return the WTSS object representation."""
        text = f'wtss(url="{self._url}",' \
               f'validate={self._validate},' \
               f'access_token={self._access_token})'

        return text

    def _ipython_key_completions_(self):
        """Integrate key completions for WTSS in IPython.

        Returns:
            list: The list of available coverages in the service.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        return self.coverages

    def _repr_html_(self):
        """Display the WTSS object as HTML.

        This integrates a rich display in IPython.
        """
        html = render_html('wtss.html', service=self)

        return html

    @staticmethod
    def _request(url, op, method: str = 'post', headers=None, params=None, json=None, verify: bool = True):
        """Query the WTSS service using HTTP GET verb and return the result as a JSON document.

        Args:
            url (str): URL for the WTSS server.
            op (str): WTSS operation.
            **params (dict): Dictionary, list of tuples or bytes to send
                in the query string for the underlying ``Requests``.

        Returns:
            A JSON document.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body does not contain a valid json or geojson.
        """
        url_components = [url, op]

        url = '/'.join(s.strip('/') for s in url_components)

        response = getattr(requests, method)(url, headers=headers, params=params, json=json, verify=verify)

        response.raise_for_status()

        return response.json()
