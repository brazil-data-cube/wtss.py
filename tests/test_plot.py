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

"""Offline tests for ``TimeSeries.plot`` using the headless Agg backend.

These tests exercise the matplotlib plotting path of :class:`wtss.timeseries.TimeSeries`
without a live server and without a display. The ``Agg`` backend is selected *before*
``matplotlib.pyplot`` is imported anywhere, so figures are rendered in memory and never
shown on screen, which is what allows the suite to run in CI.

They also pin down the three plotting bugs catalogued in ``DIAGNOSTICO.md``:

* **B10** -- ``plot`` calls ``fig.show()`` before any series is drawn.
* **B11** -- ``_limit`` is left unset when the per-attribute loop never runs.
* **B12** -- an empty ``attributes`` list reaches ``plt.subplots(0)`` and explodes.
"""

import warnings

import matplotlib

# Must be set before pyplot is imported by the client (lazy import inside plot()).
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

import pytest  # noqa: E402
import responses  # noqa: E402

from wtss import WTSS  # noqa: E402
from wtss.timeseries import TimeSeries  # noqa: E402

#: Base URL used for the mocked WTSS service.
MOCK_URL = 'http://wtss.test'

#: Timeline shared by every fixture in this module (already sorted).
TIMELINE = ['2017-01-01', '2017-01-17', '2017-02-02']

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
    'timeline': TIMELINE,
}

POINT_GEOM = {'type': 'Point', 'coordinates': [-54.0, -12.0]}

#: Single-point time series with two attributes. ``-3000`` is the nodata value of
#: both bands, so it should be masked away (rendered as ``None``) when plotting.
POINT_TS_RESPONSE = {
    'results': [
        {
            'pixel_center': POINT_GEOM,
            'pixel_size': [231.65, 231.65],
            'time_series': {
                'timeline': TIMELINE,
                'values': {'NDVI': [1000, -3000, 3000], 'EVI': [500, 600, 700]},
            },
        }
    ],
    'query': {
        'attributes': ['NDVI', 'EVI'],
        'start_datetime': '2017-01-01T00:00:00Z',
        'end_datetime': '2017-02-28T00:00:00Z',
        'geom': POINT_GEOM,
    },
}

#: Summarize payload carrying the quantile aggregations consumed by ``plot(stats=True)``.
SUMMARIZE_RESPONSE = {
    'query': {
        'attributes': ['NDVI', 'EVI'],
        'geom': POINT_GEOM,
        'aggregations': ['q1', 'q3', 'median'],
    },
    'results': {
        'timeline': TIMELINE,
        'values': {
            'NDVI': {'q1': [900, 1900, 2900], 'q3': [1100, 2100, 3100], 'median': [1000, 2000, 3000]},
            'EVI': {'q1': [450, 550, 650], 'q3': [550, 650, 750], 'median': [500, 600, 700]},
        },
    },
}


@pytest.fixture(autouse=True)
def _close_figures():
    """Avoid leaking figures across tests (and the resulting memory warning)."""
    yield
    plt.close('all')


@pytest.fixture
def service():
    """Build a WTSS client with the plotting endpoints mocked."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(responses.GET, f'{MOCK_URL}/', json=ROOT_RESPONSE, status=200)
        rsps.add(responses.GET, f'{MOCK_URL}/MOD13Q1-6', json=COVERAGE_RESPONSE, status=200)
        rsps.add(responses.POST, f'{MOCK_URL}/MOD13Q1-6/timeseries',
                 json=POINT_TS_RESPONSE, status=200)
        rsps.add(responses.POST, f'{MOCK_URL}/MOD13Q1-6/summarize',
                 json=SUMMARIZE_RESPONSE, status=200)
        yield WTSS(MOCK_URL, access_token='fake-token')


def _point_timeseries(service):
    """Return the materialised single-point :class:`TimeSeries`."""
    search = service['MOD13Q1-6'].ts(
        attributes=['NDVI'],
        geom=POINT_GEOM,
        start_datetime='2017-01-01',
        end_datetime='2017-02-28',
    )
    return search.ts


class TestPlotHappyPath:
    """A single-point plot must render one axis per attribute, fully offline."""

    def test_single_attribute_produces_one_axis(self, service):
        ts = _point_timeseries(service)
        with warnings.catch_warnings():
            # B10's premature fig.show() warns under Agg; not the subject here.
            warnings.simplefilter('ignore')
            ts.plot(attributes=['NDVI'])

        fig = plt.gcf()
        assert len(fig.axes) == 1
        assert fig._suptitle.get_text() == 'Time Series'

    def test_multiple_attributes_produce_one_axis_each(self, service):
        ts = _point_timeseries(service)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ts.plot(attributes=['NDVI', 'EVI'])

        assert len(plt.gcf().axes) == 2

    def test_stats_false_skips_quantile_lines(self, service):
        """Without stats, only the raw series line is drawn (no median/quantiles)."""
        ts = _point_timeseries(service)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ts.plot(attributes=['NDVI'], stats=False)

        axis = plt.gcf().axes[0]
        # One location => exactly one raw line; the stats block would add 3 more.
        assert len(axis.lines) == 1

    def test_stats_true_adds_quantile_and_median_lines(self, service):
        ts = _point_timeseries(service)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ts.plot(attributes=['NDVI'], stats=True)

        axis = plt.gcf().axes[0]
        # raw series (1) + q1 + q3 + median == 4 lines.
        assert len(axis.lines) == 4
        labels = [line.get_label() for line in axis.lines]
        assert 'NDVI median' in labels

    def test_nodata_is_masked_to_none(self, service):
        """The ``-3000`` nodata sample must not be plotted as a real value."""
        ts = _point_timeseries(service)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ts.plot(attributes=['NDVI'], stats=False)

        raw_line = plt.gcf().axes[0].lines[0]
        ydata = list(raw_line.get_ydata())
        # Position 1 held nodata (-3000); plot() swaps it for None and never -3000.
        assert None in ydata
        assert -3000 not in ydata


class TestPlotMultiPoint:
    """Plotting several locations exercises the ``limit`` and title branches."""

    def _multipoint_timeseries(self, service, n_points=3):
        coverage = service['MOD13Q1-6']
        results = [
            {
                'pixel_center': {'type': 'Point', 'coordinates': [-54.0 + i * 0.01, -12.0]},
                'pixel_size': [231.65, 231.65],
                'time_series': {
                    'timeline': TIMELINE,
                    'values': {'NDVI': [1000 + i, 2000 + i, 3000 + i]},
                },
            }
            for i in range(n_points)
        ]
        data = {
            'results': results,
            'query': {**POINT_TS_RESPONSE['query'], 'attributes': ['NDVI']},
        }
        return TimeSeries(coverage, data)

    def test_limit_caps_plotted_series_and_titles_it(self, service):
        ts = self._multipoint_timeseries(service, n_points=3)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            ts.plot(attributes=['NDVI'], limit=2, stats=False)

        fig = plt.gcf()
        # Only 2 of the 3 locations are drawn (stats off => no extra lines).
        assert len(fig.axes[0].lines) == 2
        assert fig._suptitle.get_text() == 'Time Series (Showing 2 of 3 points)'


class TestDeferredSearchPlot:
    """The deferred ``TimeSeriesSearch.plot`` must delegate to the materialised series."""

    def test_point_search_plot_renders(self, service):
        search = service['MOD13Q1-6'].ts(
            attributes=['NDVI'],
            geom=POINT_GEOM,
            start_datetime='2017-01-01',
            end_datetime='2017-02-28',
        )
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            # Point geometry => no pagination => delegates straight to TimeSeries.plot.
            search.plot(attributes=['NDVI'])

        assert len(plt.gcf().axes) == 1


class TestPlotValidation:
    """Argument validation on the plot entry point."""

    def test_negative_limit_raises(self, service):
        ts = _point_timeseries(service)
        with pytest.raises(ValueError, match='Limit cannot be negative'):
            ts.plot(limit=-1)


class TestPlotKnownBugs:
    """Regression coverage that pins down the catalogued plotting bugs."""

    def test_show_is_called_before_drawing_B10(self, service):
        """B10: ``plot`` triggers ``fig.show()`` (warns under the Agg backend)."""
        ts = _point_timeseries(service)
        with pytest.warns(UserWarning, match='non-interactive'):
            ts.plot(attributes=['NDVI'])

    def test_empty_attributes_break_subplots_B12(self, service):
        """B12: an empty attribute list reaches ``plt.subplots(0)`` and raises."""
        coverage = service['MOD13Q1-6']
        data = {
            'results': POINT_TS_RESPONSE['results'],
            'query': {**POINT_TS_RESPONSE['query'], 'attributes': []},
        }
        ts = TimeSeries(coverage, data)
        with pytest.raises(ValueError, match='positive integer'):
            ts.plot()

    def test_unset_limit_when_loop_never_runs_B11(self, service):
        """B11: with caller-supplied empty ``axes`` the per-attribute loop is skipped,
        leaving ``_limit`` as ``None`` and tripping ``None < len(...)``.
        """
        coverage = service['MOD13Q1-6']
        data = {
            'results': POINT_TS_RESPONSE['results'],
            'query': {**POINT_TS_RESPONSE['query'], 'attributes': []},
        }
        ts = TimeSeries(coverage, data)
        fig = plt.figure()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with pytest.raises(TypeError):
                # fig + empty axes bypass subplots(0), exposing the _limit gap.
                ts.plot(fig=fig, axes=[])
