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

"""Offline unit tests for :class:`wtss.timeseries.TimeSeries` item access.

These pin down B9: ``TimeSeries[band]`` must return a time-aligned
``pandas.Series`` (with the timeline as index and the location preserved),
instead of forcing callers to dig into the private ``_locations`` to correlate
``values(band)`` with ``timeline``.
"""

import pandas
import pytest

from wtss.timeseries import TimeSeries

TIMELINE = ['2017-01-01', '2017-01-17', '2017-02-02']


def _location(lon, lat, values):
    return {
        'pixel_center': {'type': 'Point', 'coordinates': [lon, lat]},
        'pixel_size': [231.65, 231.65],
        'time_series': {'timeline': list(TIMELINE), 'values': {'NDVI': list(values)}},
    }


def _timeseries(results):
    data = {'results': results, 'query': {'attributes': ['NDVI'], 'geom': {}}}
    # _coverage is unused by __getitem__.
    return TimeSeries(coverage=None, data=data)


class TestSinglePoint:
    """A single-location time series yields a datetime-indexed Series."""

    def test_returns_series_aligned_to_timeline(self):
        ts = _timeseries([_location(-54.0, -12.0, [1000, 2000, 3000])])
        series = ts['NDVI']

        assert isinstance(series, pandas.Series)
        assert series.name == 'NDVI'
        assert isinstance(series.index, pandas.DatetimeIndex)
        assert series.index.equals(pandas.to_datetime(TIMELINE))
        assert series.tolist() == [1000, 2000, 3000]

    def test_lookup_by_timestamp(self):
        ts = _timeseries([_location(-54.0, -12.0, [1000, 2000, 3000])])
        series = ts['NDVI']
        assert series[pandas.Timestamp('2017-01-17')] == 2000

    def test_unknown_attribute_raises_keyerror(self):
        ts = _timeseries([_location(-54.0, -12.0, [1000, 2000, 3000])])
        with pytest.raises(KeyError, match='EVI'):
            ts['EVI']


class TestMultiPoint:
    """Several locations yield a (datetime, location) MultiIndex Series."""

    def _ts(self):
        return _timeseries([
            _location(-54.0, -12.0, [1000, 2000, 3000]),
            _location(-53.99, -12.0, [1100, 2100, 3100]),
        ])

    def test_multiindex_levels(self):
        series = self._ts()['NDVI']
        assert list(series.index.names) == ['datetime', 'location']
        assert len(series) == 6  # 2 locations x 3 timestamps

    def test_select_one_location(self):
        series = self._ts()['NDVI']
        loc = series.xs((-53.99, -12.0), level='location')
        assert loc.tolist() == [1100, 2100, 3100]

    def test_unstack_to_wide_dataframe(self):
        wide = self._ts()['NDVI'].unstack('location')
        assert isinstance(wide, pandas.DataFrame)
        assert list(wide.columns) == [(-54.0, -12.0), (-53.99, -12.0)]
        assert wide.shape == (3, 2)  # 3 timestamps x 2 locations


class TestEmpty:
    """An empty time series returns an empty Series rather than raising."""

    def test_empty_results(self):
        series = _timeseries([])['NDVI']
        assert isinstance(series, pandas.Series)
        assert series.empty
