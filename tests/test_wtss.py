#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit-test for the WTSS Python Client Library for."""

from ssl import ALERT_DESCRIPTION_DECOMPRESSION_FAILURE

import conftest
from pystac_client import Client
from requests import ConnectionError as _ConnectionError

from wtss import *


class TestSucessRequests:
    """Test Query Parameters."""

    def test_timeseries_success_MOD13Q1(self, server_request_timeseries, client_request_timeseries):
        # Query WTSS Server
        server_json_response = server_request_timeseries.json()
        assert server_request_timeseries.status_code == 200

        # WTSS Python Client
        client_json_response = client_request_timeseries
        assert client_json_response.success_query

        # Validate responses
        assert client_json_response.attributes == list(server_json_response['results'][0]['time_series']['values'].keys())
        assert client_json_response.attributes == server_json_response['query']['attributes']
        assert client_json_response.number_of_pixels == len(server_json_response['results'])
        assert client_json_response.timeline == server_json_response['results'][0]['time_series']['timeline']
        assert conftest.collectionId == server_json_response['query']['collectionId']
        assert conftest.collectionId == client_json_response.query['collectionId']
        assert conftest.collectionId == client_json_response._coverage.name
        assert conftest.geom == server_json_response['query']['geom']
        assert conftest.geom == client_json_response.query['geom']
        assert conftest.start_datetime == server_json_response['query']['start_datetime']
        assert conftest.start_datetime == client_json_response.query['start_datetime']
        assert conftest.end_datetime == server_json_response['query']['end_datetime']
        assert conftest.end_datetime == client_json_response.query['end_datetime']
        assert conftest.applyAttributeScale == server_json_response['query']['applyAttributeScale']
        assert conftest.applyAttributeScale == client_json_response.query['applyAttributeScale']
        
        attr_name = client_json_response.attributes[0]
        assert client_json_response.values(attr_name)[0] == server_json_response['results'][0]['time_series']['values'][attr_name]

        df = client_json_response.pandas_dataframe()
        NDVI_1stpixel = df[(df["attribute"] == 'NDVI') & (df["pixel_id"] == 0)]['value'].tolist()
        assert NDVI_1stpixel == server_json_response['results'][0]['time_series']['values'][attr_name]


    def test_summarize_success_MOD13Q1(self, server_request_summarize, client_request_summarize):
        # Query WTSS Server
        server_json_response = server_request_summarize.json()
        assert server_request_summarize.status_code == 200

        # WTSS Python Client
        client_json_response = client_request_summarize
        assert client_json_response.success_query

        # Validate responses
        assert client_json_response.attributes == list(server_json_response['results']['values'].keys())
        assert client_json_response.attributes == server_json_response['query']['attributes']
        assert client_json_response.timeline == server_json_response['results']['timeline']
        assert conftest.collectionId == server_json_response['query']['collectionId']
        assert conftest.collectionId == client_json_response.query['collectionId']
        assert conftest.collectionId == client_json_response._coverage.name
        assert conftest.geom == server_json_response['query']['geom']
        assert conftest.geom == client_json_response.query['geom']
        assert conftest.geom == client_json_response.geometry
        assert conftest.start_datetime == server_json_response['query']['start_datetime']
        assert conftest.start_datetime == client_json_response.query['start_datetime']
        assert conftest.end_datetime == server_json_response['query']['end_datetime']
        assert conftest.end_datetime == client_json_response.query['end_datetime']
        assert conftest.applyAttributeScale == server_json_response['query']['applyAttributeScale']
        assert conftest.applyAttributeScale == client_json_response.query['applyAttributeScale']
        
        attr_name = client_json_response.attributes[0]
        assert client_json_response.values(attr_name).values('mean') == server_json_response['results']['values'][attr_name]['mean']
        
        df = client_json_response.pandas_dataframe()
        df_NDVI_mean = df[(df["attribute"] == 'NDVI') & (df["aggregation"] == 'mean')]['value'].tolist()
        assert df_NDVI_mean == server_json_response['results']['values'][attr_name]['mean']

        assert client_json_response.aggregations == server_json_response['query']['aggregations']


    def test_coverage_success_MOD13Q1(self, client_request_summarize):
        # WTSS Python Client
        client_json_response = client_request_summarize
        assert client_json_response.success_query

        # Query STAC Collection
        STAC_URL = 'https://brazildatacube.dpi.inpe.br/stac/'
        _client = Client.open(STAC_URL, parameters = dict(access_token=conftest.BDC_AUTH_CLIENT_SECRET))
        collection = _client.get_collection(conftest.collectionId)
        
        # Validate responses
        assert client_json_response._coverage.name == collection.id
        assert client_json_response._coverage.attributes == [band for band in collection.extra_fields['properties']['eo:bands']]
        assert client_json_response._coverage.crs == collection.extra_fields['bdc:crs']
        assert client_json_response._coverage.description == collection.description
        assert client_json_response._coverage.dimensions == collection.extra_fields['cube:dimensions']
        assert client_json_response._coverage.spatial_extent == collection.extent.spatial.bboxes[0]
        assert client_json_response._coverage.timeline == collection.extra_fields['cube:dimensions']['temporal']['values']