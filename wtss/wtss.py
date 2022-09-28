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


As an example, we could retrieve the time series for the ``MOD13Q1`` data
product given the ``longitude -54.0`` and ``latitude -12.0`` in the date interval
of ``January 1st, 2001`` and ``December 31st, 2003``:


    .. doctest::
        :skipif: WTSS_EXAMPLE_URL is None

        >>> from wtss import *
        >>> service = WTSS(WTSS_EXAMPLE_URL)
        >>> for cv in service:
        ...     print(cv)
        ...
        Coverage...
        ...
"""

import requests

from .coverage import Coverage
from .utils import render_html


class WTSS:
    """Implement a client for WTSS.

    .. note::

        For more information about coverage definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, url, validate=False, access_token=None):
        """Create a WTSS client attached to the given host address (an URL).

        Args:
            url (str): URL for the WTSS server.
            validate (bool, optional): If True the client will validate the server response.
            access_token (str, optional): Authentication token to be used with the WTSS server.
        """
        #: str: URL for the WTSS server.
        self._url = url

        #: bool: If True the client will validate the server response.
        self._validate = validate

        #: str: Authentication token to be used with the WTSS server.
        self._access_token = access_token

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
        return self._list_coverages()

    def _list_coverages(self):
        """List available coverages in the service.

        Returns:
            list: A list with the names of available coverages in the service.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        result = self._get(self._url, op='list_coverages')

        return result['coverages']

    def _describe_coverage(self, name):
        """Get coverage metadata for the given coverage identified by its name.

        Args:
            name (str): The coverage name identifier used to retrieve its metadata.

        Returns:
            dict: The coverage metadata as a dictionary.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        cv = self._get(self._url,
                       op='describe_coverage',
                       name=name)

        return cv

    def _time_series(self, **options):
        """Retrieve the time series for a given location.

        Keyword Args:
            attributes (optional): A string with attribute names separated by commas,
                or any sequence of strings. If omitted, the values for all
                coverage attributes are retrieved.
            longitude (int/float): A longitude value according to EPSG:4326.
            latitude (int/float): A latitude value according to EPSG:4326.
            start_date (:obj:`str`, optional): The begin of a time interval.
            end_date (:obj:`str`, optional): The begin of a time interval.

        Returns:
            dict: A time series object as a dictionary.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        ts = self._get(self._url,
                       op='time_series',
                       **options)

        return ts

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
        cv_meta = self._describe_coverage(key)

        return Coverage(service=self, metadata=cv_meta)

    def __getattr__(self, name):
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
        return self._list_coverages()

    def _repr_html_(self):
        """Display the WTSS object as HTML.

        This integrates a rich display in IPython.
        """
        cv_list = self._list_coverages()

        html = render_html('wtss.html', url=self._url, coverages=cv_list)

        return html

    def _get(self, url, op, **params):
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
        url_components = [url, 'wtss', op]

        params.setdefault('access_token', self._access_token)

        url = '/'.join(s.strip('/') for s in url_components)

        response = requests.get(url, params=params)

        response.raise_for_status()

        return response.json()
