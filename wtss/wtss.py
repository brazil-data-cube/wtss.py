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


class wtss:
    """Implement a client for WTSS.

    See https://github.com/brazil-data-cube/wtss-spec for
    more information on WTSS.

    Attributes:

        _url (str): URL for the WTSS server.
        _validate (bool): If True the client will validate the server response.
        _access_token (str): Authentication token to be used with the WTSS server.
        _coverages (dict): The list of availabl coverages in the service provider.
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
        #self._coverages = dict()


    def __iter__(self):
        """Iterate over coverages available in the service.

        Returns:
            A coverage at each iteration.
        """
        result = wtss._get(self._url, op='list_coverages')

        coverages = result['coverages']

        for cv_name in coverages:
            cv = wtss._get(self._url,
                           op='describe_coverage',
                           params={'name': cv_name})

            yield cv


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

        content_type = response.headers.get('content-type')

        # if content_type not in ('application/json', 'application/geo+json'):
        #     raise ValueError('HTTP response is not JSON: Content-Type: {}'.format(content_type))

        return response.json()

