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


    >>> from wtss import *
    >>> service = wtss('http://www.esensing.dpi.inpe.br')
    >>> for cv in service:
    ...     print(cv)
    ...
    {'name': ...}
    ...
"""

import requests

from .coverage import Coverage


class wtss:
    """Implement a client for WTSS.

    See https://github.com/brazil-data-cube/wtss-spec for
    more information on WTSS.

    Attributes:
        _url (str): URL for the WTSS server.
        _validate (bool): If True the client will validate the server response.
        _access_token (str): Authentication token to be used with the WTSS server.
    """

    def __init__(self, url, validate=False, access_token=None):
        """Create a WTSS client attached to the given host address (an URL).

        Args:
            url (str): URL for the WTSS server.
            validate (bool): If True the client will validate the server response.
            access_token (str): Authentication token to be used with the WTSS server.
        """
        self._url = url
        self._validate = validate
        self._access_token = access_token


    @property
    def coverages(self):
        """Return a list of coverage names.

        Returns:
            list: A list with the names of available coverages in the service.

        Raises:
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        return self._list_coverages()


    def _list_coverages(self):
        """List available coverages in the service.

        Returns:
            list: A list with the names of available coverages in the service.

        Raises:
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        result = wtss._get(self._url, op='list_coverages')

        return result['coverages']


    def _describe_coverage(self, name):
        """Get coverage metadata for the given coverage identified by its name.

        Args:
            name (str): The coverage name identifier used to retrieve its metadata.

        Returns:
            dict: The coverage metadata as a dictionary.

        Raises:
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        cv = wtss._get(self._url,
                       op='describe_coverage',
                       params={'name': name})

        return cv


    def _time_series(self, **kwargs):
        """Retrieve the time series for a given location.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            dict: A time series object as a dictionary.

        Raises:
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        ts = wtss._get(self._url,
                       op='time_series',
                       params=kwargs)

        return ts


    def __getitem__(self, key):
        """Get coverage whose name is identified by the key.

        Returns:
            Coverage: A coverage metadata object.

        Raises:
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
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
        """
        try:
            return self[name]
        except:
            raise AttributeError(f'No attributed name "{name}"')


    def __iter__(self):
        """Iterate over coverages available in the service.

        Returns:
            A coverage at each iteration.
        """
        coverages = self._list_coverages()

        for cv_name in coverages:
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
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
        """
        return self._list_coverages()


    def _repr_html_(self):
        """Display the WTSS object as HTML.

        This integrates a rich display in IPython.
        """
        cv_list = self._list_coverages()

        coverages = ''

        for cv_name in cv_list:
            coverages += f'<li>{cv_name}</li>'

        html = f'''\
<p>WTSS</p>
<ul>
    <li><b>URL:</b> {self._url}</li>
    <li><b>Coverages:</b></li>
    <ul>
    {coverages}
    </ul>
</ul>'''

        return html


    @staticmethod
    def _get(url, op, params=None):
        """Query the WTSS service using HTTP GET verb and return the result as a JSON document.

        Args:
            url (str): URL for the WTSS server.
            op (str): WTSS operation.
            params (dict): Dictionary, list of tuples or bytes to send
                in the query string for the underlying `Requests`.

        Returns:
            A JSON document.

        Raises:
            HTTPError: If the server response indicates an error.
            ValueError: If the response body does not contain a valid json or geojson.
        """
        url_components = [url, 'wtss', op]

        url = '/'.join(s.strip('/') for s in url_components)

        response = requests.get(url, params=params)

        response.raise_for_status()

        return response.json()
