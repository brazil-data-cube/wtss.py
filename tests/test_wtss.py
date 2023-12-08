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

"""Unit-test for the WTSS Python Client Library for."""

from ssl import ALERT_DESCRIPTION_DECOMPRESSION_FAILURE
from urllib.error import HTTPError

import conftest
import requests
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
        assert conftest.COLLECTIONID == server_json_response['query']['collectionId']
        assert conftest.COLLECTIONID == client_json_response.query['collectionId']
        assert conftest.COLLECTIONID == client_json_response._coverage.name
        assert conftest.GEOMETRY == server_json_response['query']['geom']
        assert conftest.GEOMETRY == client_json_response.query['geom']
        assert conftest.START_DATETIME == server_json_response['query']['start_datetime']
        assert conftest.START_DATETIME == client_json_response.query['start_datetime']
        assert conftest.END_DATETIME == server_json_response['query']['end_datetime']
        assert conftest.END_DATETIME == client_json_response.query['end_datetime']
        assert conftest.APPLYATTRIBUTESCALE == server_json_response['query']['applyAttributeScale']
        assert conftest.APPLYATTRIBUTESCALE == client_json_response.query['applyAttributeScale']
        
        attr_name = client_json_response.attributes[0]
        assert client_json_response.values(attr_name)[0] == server_json_response['results'][0]['time_series']['values'][attr_name]

        df = client_json_response.df()
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
        assert conftest.COLLECTIONID == server_json_response['query']['collectionId']
        assert conftest.COLLECTIONID == client_json_response.query['collectionId']
        assert conftest.COLLECTIONID == client_json_response._coverage.name
        assert conftest.GEOMETRY == server_json_response['query']['geom']
        assert conftest.GEOMETRY == client_json_response.query['geom']
        assert conftest.GEOMETRY == client_json_response.geometry
        assert conftest.START_DATETIME == server_json_response['query']['start_datetime']
        assert conftest.START_DATETIME == client_json_response.query['start_datetime']
        assert conftest.END_DATETIME == server_json_response['query']['end_datetime']
        assert conftest.END_DATETIME == client_json_response.query['end_datetime']
        assert conftest.APPLYATTRIBUTESCALE == server_json_response['query']['applyAttributeScale']
        assert conftest.APPLYATTRIBUTESCALE == client_json_response.query['applyAttributeScale']
        
        attr_name = client_json_response.attributes[0]
        assert client_json_response.values(attr_name).values('mean') == server_json_response['results']['values'][attr_name]['mean']
        
        df = client_json_response.df()
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
        collection = _client.get_collection(conftest.COLLECTIONID)
        
        # Validate responses
        assert client_json_response._coverage.name == collection.id
        assert client_json_response._coverage.attributes == [band for band in collection.extra_fields['properties']['eo:bands']]
        assert client_json_response._coverage.crs == collection.extra_fields['bdc:crs']
        assert client_json_response._coverage.description == collection.description
        assert client_json_response._coverage.dimensions == collection.extra_fields['cube:dimensions']
        assert client_json_response._coverage.spatial_extent == collection.extent.spatial.bboxes[0]
        assert client_json_response._coverage.timeline == collection.extra_fields['cube:dimensions']['temporal']['values']


class TestDifferentGeometries:
    """Test GeoJSON Geometries."""

    # GeoJSON examples
    GeoJSON_Point_valid = {"type":"Point","coordinates":[-54,-12]}
    GeoJSON_Point_Nowhere = {"type":"Point","coordinates":[0,0]}
    GeoJSON_Polygon_Valid = {"type": "Polygon","coordinates": [[[-54,-12],[-53.99,-12],[-53.99,-11.99],[-54,-11.99],[-54,-12]]]}
    GeoJSON_Polygon_Nowhere = {"type": "Polygon","coordinates": [[[-88,-88],[-87.99,-88],[-87.99,-87.99],[-88,-87.99],[-88,-88]]]}
    GeoJSON_LineString = {"type":"LineString","coordinates":[[-54,-12],[-53.99,-11.99]]}
    GeoJSON_MultiLineString = {"type":"MultiLineString","coordinates":[[[-10,-75],[-10,75]],[[10,-75],[10,75]],[[-75,-100],[75,-100]],[[-75,100],[75,100]]]}
    GeoJSON_MultiPolygon = {"type":"MultiPolygon","coordinates":[[[[-50,60],[-30,60],[-30,80],[-50,80],[-50,60]]],[[[-20,60],[0,60],[0,80],[-20,80],[-20,60]]],[[[10,60],[30,60],[30,80],[10,80],[10,60]]]]}
    GeoJSON_GeometryCollection = {"type":"GeometryCollection","geometries":[{"type":"LineString","coordinates":[[-50,-50],[0,-50]]},{"type":"Point","coordinates":[40,-50]},{"type":"Polygon","coordinates":[[[10,-60],[30,-60],[20,-40],[10,-60]]]}]}

    def test_GeoJSON_valid_Point(self):
        # Query to python WTSS client
        client_json_response = conftest.ClientRequestGeometry.client_request_geometry(self.GeoJSON_Point_valid)
        assert client_json_response.success_query
        assert client_json_response.geometry == self.GeoJSON_Point_valid

    def test_GeoJSON_valid_Polygon(self):
        # Query to python WTSS client
        client_json_response = conftest.ClientRequestGeometry.client_request_geometry(self.GeoJSON_Polygon_Valid)
        assert client_json_response.success_query
        assert client_json_response.geometry == self.GeoJSON_Polygon_Valid

    def test_GeoJSON_LineString(self):
        # Query to python WTSS client
        client_json_response = conftest.ClientRequestGeometry.client_request_geometry(self.GeoJSON_LineString)

        assert type(client_json_response) == requests.exceptions.HTTPError
        response = client_json_response.response
        assert response.status_code == 400
        assert response.json()['description'] == "The only geometry formats allowed are Point and Polygon."
        assert response.json()['code'] == 400

    def test_GeoJSON_MultiLineString(self):
        # Query to python WTSS client
        client_json_response = conftest.ClientRequestGeometry.client_request_geometry(self.GeoJSON_MultiLineString)

        assert type(client_json_response) == requests.exceptions.HTTPError
        response = client_json_response.response
        assert response.status_code == 400
        assert response.json()['description'] == "The only geometry formats allowed are Point and Polygon."
        assert response.json()['code'] == 400

    def test_GeoJSON_MultiPolygon(self):
        # Query to python WTSS client
        client_json_response = conftest.ClientRequestGeometry.client_request_geometry(self.GeoJSON_MultiPolygon)

        assert type(client_json_response) == requests.exceptions.HTTPError
        response = client_json_response.response
        assert response.status_code == 400
        assert response.json()['description'] == "The only geometry formats allowed are Point and Polygon."
        assert response.json()['code'] == 400

    def test_GeoJSON_GeometryCollection(self):
        # Query to python WTSS client
        client_json_response = conftest.ClientRequestGeometry.client_request_geometry(self.GeoJSON_GeometryCollection)

        assert type(client_json_response) == requests.exceptions.HTTPError
        response = client_json_response.response
        assert response.status_code == 400
        assert response.json()['description'] == "The only geometry formats allowed are Point and Polygon."
        assert response.json()['code'] == 400