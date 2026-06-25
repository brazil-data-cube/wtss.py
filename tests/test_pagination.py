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

"""Offline tests for the automatic pagination of ``TimeSeriesSearch``.

Pagination is triggered for any geometry that is not a single ``Point`` (polygon and
multipoint queries). The server answers each page with a ``pagination`` block describing
``next`` / ``total_pages``; the client walks those pages and concatenates the per-location
series. Here we mock three ordered pages with the ``responses`` library -- they are served
in registration order to the single ``.../timeseries`` endpoint -- and assert that the
materialised :class:`wtss.timeseries.TimeSeries` stitches every page back together.
"""

import pytest
import responses

from wtss import WTSS

MOCK_URL = 'http://wtss.test'

#: The three pages cover three consecutive dates; the coverage timeline holds all of them.
FULL_TIMELINE = ['2017-01-01', '2017-02-02', '2017-03-06']

ROOT_RESPONSE = {
    'wtss_version': '2.0',
    'links': [
        {'rel': 'self', 'title': 'WTSS', 'href': f'{MOCK_URL}/'},
        {'rel': 'data', 'title': 'Coverage MOD13Q1-6', 'href': f'{MOCK_URL}/MOD13Q1-6'},
    ],
}

COVERAGE_RESPONSE = {
    'fullname': 'MOD13Q1-6',
    'description': 'MODIS Vegetation Indices 16-day 250m (MOD13Q1) v6.',
    'bands': [{'name': 'NDVI', 'nodata': -3000, 'data_type': 'int16'}],
    'bdc:crs': '+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181',
    'raster_size': {'xsize': 172800, 'ysize': 86400},
    'extent': {
        'type': 'Polygon',
        'coordinates': [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
    },
    'timeline': FULL_TIMELINE,
}

#: A polygon over a single pixel -- enough to enable pagination (geom != Point) while
#: keeping a single location whose series grows page after page.
POLYGON_GEOM = {
    'type': 'Polygon',
    'coordinates': [[[-54, -12], [-53.99, -12], [-53.99, -11.99], [-54, -11.99], [-54, -12]]],
}

#: Centre of the one pixel matched by the polygon; identical across pages so the client
#: keys every page to the same :class:`Location` and extends it.
PIXEL_CENTER = {'type': 'Point', 'coordinates': [-54.0, -12.0]}

_QUERY = {
    'attributes': ['NDVI'],
    'start_datetime': '2017-01-01T00:00:00Z',
    'end_datetime': '2017-03-31T00:00:00Z',
    'geom': POLYGON_GEOM,
}


def _page(timeline, values, *, next_page, total_pages=3):
    """Build a single paginated time series response for the one pixel."""
    return {
        'results': [
            {
                'pixel_center': PIXEL_CENTER,
                'pixel_size': [231.65, 231.65],
                'time_series': {'timeline': list(timeline), 'values': {'NDVI': list(values)}},
            }
        ],
        'query': dict(_QUERY),
        'pagination': {
            'next': next_page,
            'total_pages': total_pages,
            'start_datetime': _QUERY['start_datetime'],
            'end_datetime': _QUERY['end_datetime'],
        },
    }


#: Page 1 announces two more pages; pages 2 and 3 each add one timestamp.
PAGE_1 = _page(['2017-01-01'], [1000], next_page=2)
PAGE_2 = _page(['2017-02-02'], [2000], next_page=3)
PAGE_3 = _page(['2017-03-06'], [3000], next_page=None)


@pytest.fixture
def service():
    """WTSS client whose ``timeseries`` endpoint replays the three pages in order."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(responses.GET, f'{MOCK_URL}/', json=ROOT_RESPONSE, status=200)
        rsps.add(responses.GET, f'{MOCK_URL}/MOD13Q1-6', json=COVERAGE_RESPONSE, status=200)
        # Ordered registration: responses serves these FIFO for the three POST calls.
        for page in (PAGE_1, PAGE_2, PAGE_3):
            rsps.add(responses.POST, f'{MOCK_URL}/MOD13Q1-6/timeseries', json=page, status=200)
        yield WTSS(MOCK_URL, access_token='fake-token')


def _search(service):
    return service['MOD13Q1-6'].ts(**_QUERY)


class TestPaginationDetection:
    """Pagination must be enabled only for non-point geometries."""

    def test_polygon_enables_pagination(self, service):
        search = _search(service)
        # total_locations() fetches page 1 and records the pagination block.
        assert search.total_locations() == 1
        assert search._pagination is not None
        assert search._pagination['total_pages'] == 3

    def test_point_disables_pagination(self, service):
        search = service['MOD13Q1-6'].ts(
            attributes=['NDVI'],
            geom={'type': 'Point', 'coordinates': [-54.0, -12.0]},
            start_datetime='2017-01-01',
            end_datetime='2017-03-31',
        )
        # A single Point never paginates, regardless of the server's pagination block.
        assert search._pagination_allowed() is False


class TestPaginationStitching:
    """Walking the pages must concatenate the per-location series in order."""

    def test_ts_concatenates_every_page(self, service):
        ts = _search(service).ts
        assert ts.timeline == FULL_TIMELINE
        # A single location whose NDVI series spans all three pages.
        assert ts.values('NDVI') == [[1000, 2000, 3000]]

    def test_iterator_yields_one_timeseries_per_page(self, service):
        search = _search(service)
        # iterator() reads self._pagination before priming it, so callers must
        # materialise page 1 first (which is exactly what the .ts property does).
        search.total_locations()
        pages = list(search.iterator())
        # First yield is page 1 (already loaded), then pages 2 and 3.
        assert len(pages) == 3

    def test_dataframe_spans_full_timeline(self, service):
        df = _search(service).df()
        assert df['value'].tolist() == [1000, 2000, 3000]
        assert df['datetime'].dt.strftime('%Y-%m-%d').tolist() == FULL_TIMELINE
        assert len(df) == 3
