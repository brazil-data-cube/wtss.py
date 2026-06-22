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

"""Offline tests for the WTSS client using a mocked HTTP server.

These tests replace the live BDC server with canned JSON responses (via the
``responses`` library), so they run with no network access and no access
token. They are the foundation for measurable, CI-friendly coverage.
"""

import pytest
import responses

from wtss import WTSS

#: Base URL used for the mocked WTSS service.
MOCK_URL = 'http://wtss.test'

#: Response for the service root (GET <base>/). ``coverages`` is built from the
#: links whose ``rel == 'data'``, taking the last token of each ``title``.
ROOT_RESPONSE = {
    'wtss_version': '2.0',
    'links': [
        {'rel': 'self', 'title': 'WTSS', 'href': f'{MOCK_URL}/'},
        {'rel': 'data', 'title': 'Coverage MOD13Q1-6', 'href': f'{MOCK_URL}/MOD13Q1-6'},
        {'rel': 'data', 'title': 'Coverage S2-16D-2', 'href': f'{MOCK_URL}/S2-16D-2'},
    ],
}

#: Response for a coverage description (GET <base>/MOD13Q1-6). The timeline is
#: intentionally out of order to exercise ``Coverage.timeline`` sorting.
COVERAGE_RESPONSE = {
    'fullname': 'MOD13Q1-6',
    'description': 'MODIS Vegetation Indices 16-day 250m (MOD13Q1) v6.',
    'bands': [
        {'name': 'NDVI', 'nodata': -3000, 'data_type': 'int16'},
        {'name': 'EVI', 'nodata': -3000, 'data_type': 'int16'},
    ],
    'bdc:crs': '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181',
    'raster_size': {'xsize': 172800, 'ysize': 86400},
    'extent': {
        'type': 'Polygon',
        'coordinates': [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
    },
    'timeline': ['2017-01-17', '2017-01-01', '2017-02-02'],
}

#: GeoJSON point used by the time series / summarize queries.
POINT_GEOM = {'type': 'Point', 'coordinates': [-54.0, -12.0]}

#: Response for a time series query (POST <base>/MOD13Q1-6/timeseries). The
#: location timeline matches the in-range coverage timeline, so no pagination
#: is triggered for this single-point query.
TIMESERIES_RESPONSE = {
    'results': [
        {
            'pixel_center': {'type': 'Point', 'coordinates': [-54.0, -12.0]},
            'pixel_size': [231.65, 231.65],
            'time_series': {
                'timeline': ['2017-01-01', '2017-01-17', '2017-02-02'],
                'values': {'NDVI': [1000, 2000, 3000]},
            },
        }
    ],
    'query': {
        'attributes': ['NDVI'],
        'start_datetime': '2017-01-01T00:00:00Z',
        'end_datetime': '2017-02-28T00:00:00Z',
        'geom': POINT_GEOM,
    },
}

#: Response for a summarize query (POST <base>/MOD13Q1-6/summarize).
SUMMARIZE_RESPONSE = {
    'query': {
        'attributes': ['NDVI'],
        'geom': POINT_GEOM,
        'aggregations': ['mean', 'std'],
    },
    'results': {
        'timeline': ['2017-01-01', '2017-01-17', '2017-02-02'],
        'values': {
            'NDVI': {'mean': [0.5, 0.6, 0.7], 'std': [0.1, 0.1, 0.1]},
        },
    },
}


def _register_root(rsps):
    """Register the mocked service root endpoint."""
    rsps.add(responses.GET, f'{MOCK_URL}/', json=ROOT_RESPONSE, status=200)


def _register_coverage(rsps):
    """Register the mocked coverage description endpoint."""
    rsps.add(responses.GET, f'{MOCK_URL}/MOD13Q1-6', json=COVERAGE_RESPONSE, status=200)


def _register_timeseries(rsps):
    """Register the mocked time series endpoint."""
    rsps.add(responses.POST, f'{MOCK_URL}/MOD13Q1-6/timeseries',
             json=TIMESERIES_RESPONSE, status=200)


def _register_summarize(rsps):
    """Register the mocked summarize endpoint."""
    rsps.add(responses.POST, f'{MOCK_URL}/MOD13Q1-6/summarize',
             json=SUMMARIZE_RESPONSE, status=200)


@pytest.fixture
def service():
    """Build a WTSS client with every mocked endpoint registered.

    ``assert_all_requests_are_fired=False`` because individual tests only
    exercise a subset of the endpoints (e.g. the unknown-coverage test never
    reaches the coverage endpoint).
    """
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        _register_root(rsps)
        _register_coverage(rsps)
        _register_timeseries(rsps)
        _register_summarize(rsps)
        yield WTSS(MOCK_URL, access_token='fake-token')


class TestServiceRoot:
    """The client must parse the service root without a live server."""

    @responses.activate
    def test_construct_does_not_raise(self):
        _register_root(responses.mock)
        wtss = WTSS(MOCK_URL, access_token='fake-token')
        assert wtss is not None

    @responses.activate
    def test_version_parsed(self):
        _register_root(responses.mock)
        wtss = WTSS(MOCK_URL, access_token='fake-token')
        assert wtss._version == '2.0'

    @responses.activate
    def test_coverages_listed(self):
        _register_root(responses.mock)
        wtss = WTSS(MOCK_URL, access_token='fake-token')
        assert wtss.coverages == ['MOD13Q1-6', 'S2-16D-2']


class TestCoverageMetadata:
    """Fetching a coverage must yield a fully-populated Coverage object."""

    def test_getitem_returns_coverage(self, service):
        cv = service['MOD13Q1-6']
        assert cv.name == 'MOD13Q1-6'

    def test_unknown_coverage_raises_keyerror(self, service):
        with pytest.raises(KeyError):
            service['DOES-NOT-EXIST']

    def test_description(self, service):
        cv = service['MOD13Q1-6']
        assert 'MODIS' in cv.description

    def test_attributes(self, service):
        cv = service['MOD13Q1-6']
        names = [band['name'] for band in cv.attributes]
        assert names == ['NDVI', 'EVI']

    def test_crs(self, service):
        cv = service['MOD13Q1-6']
        assert cv.crs.startswith('+proj=sinu')

    def test_dimensions(self, service):
        cv = service['MOD13Q1-6']
        assert cv.dimensions == {'xsize': 172800, 'ysize': 86400}

    def test_timeline_is_sorted(self, service):
        cv = service['MOD13Q1-6']
        assert cv.timeline == ['2017-01-01', '2017-01-17', '2017-02-02']

    def test_spatial_extent_is_geometry(self, service):
        cv = service['MOD13Q1-6']
        # shapely geometry exposes a bounds tuple (minx, miny, maxx, maxy).
        assert cv.spatial_extent.bounds == (-180.0, -90.0, 180.0, 90.0)


def _search(service):
    """Build a deferred time series search for the mocked point."""
    return service['MOD13Q1-6'].ts(
        attributes=['NDVI'],
        geom=POINT_GEOM,
        start_datetime='2017-01-01',
        end_datetime='2017-02-28',
    )


class TestTimeSeries:
    """The time series endpoint must be consumed fully offline."""

    def test_ts_is_deferred(self, service):
        from wtss.timeseries_search import TimeSeriesSearch
        assert isinstance(_search(service), TimeSeriesSearch)

    def test_total_locations(self, service):
        assert _search(service).total_locations() == 1

    def test_timeseries_attributes_and_timeline(self, service):
        ts = _search(service).ts
        assert ts.attributes == ['NDVI']
        assert ts.timeline == ['2017-01-01', '2017-01-17', '2017-02-02']

    def test_timeseries_values(self, service):
        ts = _search(service).ts
        # values(attr) returns one list per location; here a single point.
        assert ts.values('NDVI') == [[1000, 2000, 3000]]

    def test_dataframe(self, service):
        df = _search(service).df()
        assert list(df.columns) == ['attribute', 'geometry', 'value', 'datetime']
        assert len(df) == 3
        assert df['value'].tolist() == [1000, 2000, 3000]


class TestSummarize:
    """The summarize endpoint must be consumed fully offline."""

    def _summarize(self, service):
        return service['MOD13Q1-6'].summarize(
            attributes=['NDVI'],
            geom=POINT_GEOM,
            start_datetime='2017-01-01',
            end_datetime='2017-02-28',
            aggregations=['mean', 'std'],
        )

    def test_success_query(self, service):
        assert self._summarize(service).success_query is True

    def test_attributes_and_aggregations(self, service):
        summ = self._summarize(service)
        assert summ.attributes == ['NDVI']
        assert summ.aggregations == ['mean', 'std']

    def test_timeline(self, service):
        summ = self._summarize(service)
        assert summ.timeline == ['2017-01-01', '2017-01-17', '2017-02-02']

    def test_values(self, service):
        summ = self._summarize(service)
        assert summ.values('NDVI').values('mean') == [0.5, 0.6, 0.7]
        assert summ.values('NDVI').values('std') == [0.1, 0.1, 0.1]

    def test_dataframe(self, service):
        df = self._summarize(service).df()
        # 1 attribute x 3 timestamps x 2 aggregations = 6 rows.
        assert list(df.columns) == ['attribute', 'aggregation', 'datetime', 'value']
        assert len(df) == 6
