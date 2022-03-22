#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
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
import os
from distutils.util import strtobool
from urllib.parse import urljoin

import requests
from pystac_client import Client

from .coverage import Coverage
from .utils import render_html


class WTSS:
    """Implement a client for WTSS.

    .. note::

        For more information about coverage definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, url: str,
                 stac_url: str = 'https://brazildatacube.dpi.inpe.br/stac/',
                 validate=False, access_token: str = None,
                 headers=None):
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

        parameters = dict(access_token=access_token)
        self._stac = Client.open(stac_url, headers=headers, parameters=parameters)

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
        collections = self._stac.get_collections()
        return [collection.id for collection in collections]

    def _time_series(self, coverage: str, **options):
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
        url = urljoin(self._url.rstrip('/') + '/', coverage)
        headers = {'x-api-key': self._access_token}
        ts = WTSS._request(url,
                           op='timeseries',
                           headers=headers,
                           **options)

        return ts

    def _summarize(self, **options):
        """Retrieve the time series summarization for a given geometry.

        Keyword Args:
            attributes (optional): A string with attribute names separated by commas,
                or any sequence of strings. If omitted, the values for all
                coverage attributes are retrieved.
            longitude (int/float): A longitude value according to EPSG:4326.
            latitude (int/float): A latitude value according to EPSG:4326.
            start_date (:obj:`str`, optional): The begin of a time interval.
            end_date (:obj:`str`, optional): The begin of a time interval.
            aggregations (:obj:`str`, optional): The list of aggregate functions to be applied over time series.

        Returns:
            dict: A time series object as a dictionary containing the summarization.

        Raises:
            ConnectionError: If the server is not reachable.
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        ts = WTSS._get(self._url,
                       op='summarize',
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
        collection = self._stac.get_collection(key)

        return Coverage(service=self, metadata=collection.to_dict())

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
        except:
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
        cv_list = self.coverages

        html = render_html('wtss.html', url=self._url, coverages=cv_list)

        return html

    @staticmethod
    def _request(url, op, method: str = 'post', headers=None, **params):
        """Query the WTSS service using HTTP GET verb and return the result as a JSON document.

        Args:
            url (str): URL for the WTSS server.
            op (str): WTSS operation.
            params (dict): Dictionary, list of tuples or bytes to send
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
        verify = bool(strtobool(os.getenv('REQUEST_SSL_VERIFY', '1')))

        response = getattr(requests, method)(url, headers=headers, json=params, verify=verify)

        response.raise_for_status()

        return response.json()
