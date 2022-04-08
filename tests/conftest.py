#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit-test configuration for the WTSS Python Client Library for."""

import os
from ssl import ALERT_DESCRIPTION_DECOMPRESSION_FAILURE

import pytest
import requests
from requests import ConnectionError as _ConnectionError

from wtss import *

WTSS_SERVER_URL = os.getenv("WTSS_SERVER_URL", None)
BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)

# Set query parameters
collectionId = 'MOD13Q1-6'
attributes = ["NDVI","EVI"]
start_datetime = '2017-01-01T00:00:00Z'
end_datetime = '2017-02-01T00:00:00Z'
geom = {"type": "Polygon","coordinates": [[[-54,-12],[-53.99,-12],[-53.99,-11.99],[-54,-11.99],[-54,-12]]]}
applyAttributeScale = False
aggregations = ['mean','std']



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



@pytest.fixture
def server_request_timeseries():
    """Get server timeseries to use as fixture."""
    response = WTSSrequest.make_request(
        'POST',
        collectionId = collectionId,
        parameters = {
            'attributes': attributes,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'geom': geom,
            'applyAttributeScale': applyAttributeScale
        },
        headers = {'x-api-key': BDC_AUTH_CLIENT_SECRET},
        route='timeseries'
    )
    return response#.json()


@pytest.fixture
def server_request_summarize():
    """Get server summarize to use as fixture."""
    response = WTSSrequest.make_request(
        'POST',
        collectionId = collectionId,
        parameters = {
            'attributes': attributes,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'geom': geom,
            'applyAttributeScale': applyAttributeScale,
            'aggregations': aggregations
        },
        headers = {'x-api-key': BDC_AUTH_CLIENT_SECRET},
        route='summarize'
    )
    return response#.json()


@pytest.fixture
def client_request_timeseries():
    """Get client timeseries to use as fixture."""
    # WTSS Python Client
    service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)
    coverage = service[collectionId]
    timeseries = coverage.ts(
        attributes = attributes,
        geom = geom,
        start_datetime = start_datetime,
        end_datetime = end_datetime,
        applyAttributeScale = applyAttributeScale
    )
    return timeseries


@pytest.fixture
def client_request_summarize():
    """Get client summarize to use as fixture."""
    # WTSS Python Client
    service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)
    coverage = service[collectionId]
    summarize = coverage.summarize(
        attributes = attributes,
        geom = geom,
        start_datetime = start_datetime,
        end_datetime = end_datetime,
        applyAttributeScale = applyAttributeScale,
        aggregations = aggregations
    )
    return summarize