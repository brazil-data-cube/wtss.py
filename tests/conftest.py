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

"""Unit-test configuration for the WTSS Python Client Library for."""

import os
from ssl import ALERT_DESCRIPTION_DECOMPRESSION_FAILURE

import pytest
import requests

from wtss import *

WTSS_SERVER_URL = os.getenv("WTSS_SERVER_URL", None)
BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)

# Set query parameters
COLLECTIONID = 'MOD13Q1-6'
ATTRIBUTES = ["NDVI","EVI"]
START_DATETIME = '2017-01-01T00:00:00Z'
END_DATETIME = '2017-02-01T00:00:00Z'
GEOMETRY = {"type": "Polygon","coordinates": [[[-54,-12],[-53.99,-12],[-53.99,-11.99],[-54,-11.99],[-54,-12]]]}
APPLYATTRIBUTESCALE = False
AGGREGATIONS = ['mean','std']



class WTSSrequest:
    """GET and POST request method."""
    
    def make_request(GETorPOST, collectionId, parameters, headers, route):
        """Make a WTSS request."""
        query_string = ""

        if GETorPOST == 'GET':
            if len(parameters) > 0:
                query_string = "?" + "&".join(['{}={}'.format(key, value) for (key, value) in parameters.items()])

            url = WTSS_SERVER_URL + collectionId + '/' + route + query_string
            return requests.get(url)
        
        elif GETorPOST == 'POST':
            url = WTSS_SERVER_URL + collectionId + '/' + route
            return requests.post(url=url, json=parameters, headers=headers)

class ClientRequestGeometry:
    """Query client with different geometries."""

    def client_request_geometry(geom):
        """Make a request to client."""
        try:
            # WTSS Python Client
            service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)
            coverage = service[COLLECTIONID]
            summarize = coverage.summarize(
                attributes = ATTRIBUTES,
                geom = geom,
                start_datetime = START_DATETIME,
                end_datetime = END_DATETIME,
                applyAttributeScale = APPLYATTRIBUTESCALE,
                aggregations = AGGREGATIONS
            )
            return summarize
        except requests.exceptions.HTTPError as err:
            return err



@pytest.fixture
def server_request_timeseries():
    """Get server timeseries to use as fixture."""
    response = WTSSrequest.make_request(
        'POST',
        collectionId = COLLECTIONID,
        parameters = {
            'attributes': ATTRIBUTES,
            'start_datetime': START_DATETIME,
            'end_datetime': END_DATETIME,
            'geom': GEOMETRY,
            'applyAttributeScale': APPLYATTRIBUTESCALE
        },
        headers = {'x-api-key': BDC_AUTH_CLIENT_SECRET},
        route='timeseries'
    )
    return response


@pytest.fixture
def server_request_summarize():
    """Get server summarize to use as fixture."""
    response = WTSSrequest.make_request(
        'POST',
        collectionId = COLLECTIONID,
        parameters = {
            'attributes': ATTRIBUTES,
            'start_datetime': START_DATETIME,
            'end_datetime': END_DATETIME,
            'geom': GEOMETRY,
            'applyAttributeScale': APPLYATTRIBUTESCALE,
            'aggregations': AGGREGATIONS
        },
        headers = {'x-api-key': BDC_AUTH_CLIENT_SECRET},
        route='summarize'
    )
    return response


@pytest.fixture
def client_request_timeseries():
    """Get client timeseries to use as fixture."""
    # WTSS Python Client
    service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)
    coverage = service[COLLECTIONID]
    timeseries = coverage.ts(
        attributes = ATTRIBUTES,
        geom = GEOMETRY,
        start_datetime = START_DATETIME,
        end_datetime = END_DATETIME,
        applyAttributeScale = APPLYATTRIBUTESCALE
    )
    return timeseries


@pytest.fixture
def client_request_summarize():
    """Get client summarize to use as fixture."""
    # WTSS Python Client
    service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)
    coverage = service[COLLECTIONID]
    summarize = coverage.summarize(
        attributes = ATTRIBUTES,
        geom = GEOMETRY,
        start_datetime = START_DATETIME,
        end_datetime = END_DATETIME,
        applyAttributeScale = APPLYATTRIBUTESCALE,
        aggregations = AGGREGATIONS
    )
    return summarize