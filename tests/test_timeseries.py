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


def _location_multi(lon, lat, values_by_attr):
    return {
        'pixel_center': {'type': 'Point', 'coordinates': [lon, lat]},
        'pixel_size': [231.65, 231.65],
        'time_series': {'timeline': list(TIMELINE),
                        'values': {k: list(v) for k, v in values_by_attr.items()}},
    }


def _timeseries(results, attributes=None):
    data = {'results': results,
            'query': {'attributes': attributes or ['NDVI'], 'geom': {}}}
    # _coverage is unused by __getitem__/df.
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


class TestDataFrameLong:
    """df(format='long') yields one row per (datetime, attribute, location)."""

    def test_single_point_two_attributes(self):
        ts = _timeseries(
            [_location_multi(-54.0, -12.0, {'NDVI': [1000, 2000, 3000],
                                            'EVI': [10, 20, 30]})],
            attributes=['NDVI', 'EVI'],
        )
        df = ts.df()  # long is the default
        assert list(df.index.names) == ['datetime', 'attribute', 'location']
        assert list(df.columns) == ['value']
        assert len(df) == 6  # 2 attributes x 3 timestamps x 1 location
        # Order is attribute-major, then timeline: NDVI@(t0,t1,t2), EVI@(t0,t1,t2).
        assert df['value'].tolist() == [1000, 2000, 3000, 10, 20, 30]

    def test_multipoint(self):
        ts = _timeseries([
            _location_multi(-54.0, -12.0, {'NDVI': [1000, 2000, 3000]}),
            _location_multi(-53.99, -12.0, {'NDVI': [1100, 2100, 3100]}),
        ])
        df = ts.df(format='long')
        assert len(df) == 6  # 1 attribute x 3 timestamps x 2 locations


class TestDataFrameWide:
    """df(format='wide') is indexed by datetime with attribute/location columns."""

    def test_single_point_columns_are_attributes(self):
        ts = _timeseries(
            [_location_multi(-54.0, -12.0, {'NDVI': [1000, 2000, 3000],
                                            'EVI': [10, 20, 30]})],
            attributes=['NDVI', 'EVI'],
        )
        df = ts.df(format='wide')
        assert isinstance(df.index, pandas.DatetimeIndex)
        assert list(df.columns) == ['NDVI', 'EVI']
        assert df.loc[pandas.Timestamp('2017-02-02'), 'NDVI'] == 3000

    def test_multipoint_columns_are_attribute_location(self):
        ts = _timeseries([
            _location_multi(-54.0, -12.0, {'NDVI': [1000, 2000, 3000]}),
            _location_multi(-53.99, -12.0, {'NDVI': [1100, 2100, 3100]}),
        ])
        df = ts.df(format='wide')
        assert list(df.columns.names) == ['attribute', 'location']
        assert df.shape == (3, 2)  # 3 timestamps x (1 attribute x 2 locations)
        assert df[('NDVI', (-53.99, -12.0))].tolist() == [1100, 2100, 3100]

    def test_invalid_format_raises(self):
        ts = _timeseries([_location_multi(-54.0, -12.0, {'NDVI': [1, 2, 3]})])
        with pytest.raises(ValueError, match="format must be"):
            ts.df(format='tall')
