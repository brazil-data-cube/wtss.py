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

"""Offline unit tests for :class:`wtss.summarize.Summarize`.

These build a ``Summarize`` directly from a canned payload (no server, no
coverage needed for the paths under test) to pin down three catalogued bugs:

* **B8**  -- ``timeline`` was a property declaring unusable ``as_date``/``fmt`` args.
* **B15** -- ``df()`` forced ``%Y-%m-%d`` and broke on ISO 8601 timestamps.
* **B17** -- argument errors were raised as bare ``Exception`` instead of
  ``TypeError`` / ``ValueError``.
"""

import inspect

import matplotlib

matplotlib.use('Agg')

import pytest  # noqa: E402

from wtss.summarize import Summarize  # noqa: E402


def _summarize(timeline=None):
    """Build a Summarize from a minimal, server-shaped payload."""
    data = {
        'query': {'attributes': ['NDVI'], 'aggregations': ['mean', 'std']},
        'results': {
            'timeline': timeline or ['2017-01-01', '2017-01-17'],
            'values': {'NDVI': {'mean': [0.5, 0.6], 'std': [0.1, 0.2]}},
        },
    }
    # _coverage is unused by the paths exercised here.
    return Summarize(coverage=None, data=data)


class TestTimelineProperty:
    """B8: ``timeline`` is a plain property with no phantom arguments."""

    def test_timeline_returns_values(self):
        assert _summarize().timeline == ['2017-01-01', '2017-01-17']

    def test_timeline_has_no_phantom_args(self):
        params = list(inspect.signature(Summarize.timeline.fget).parameters)
        assert params == ['self']


class TestDataFrameDatetime:
    """B15: ``df()`` must accept ISO 8601 timestamps, not only ``%Y-%m-%d``."""

    def test_iso8601_timeline_is_parsed(self):
        summ = _summarize(timeline=['2017-01-01T00:00:00Z', '2017-01-17T00:00:00Z'])
        df = summ.df()
        assert len(df) == 4  # 1 attribute x 2 timestamps x 2 aggregations
        assert str(df['datetime'].dtype).startswith('datetime64')

    def test_date_only_timeline_still_works(self):
        df = _summarize().df()
        # Each timestamp repeats once per aggregation (mean, std).
        dates = sorted(set(df['datetime'].dt.strftime('%Y-%m-%d')))
        assert dates == ['2017-01-01', '2017-01-17']


class TestArgumentErrors:
    """B17: plotting argument checks raise specific exception types."""

    def test_plot_attributes_must_be_list(self):
        with pytest.raises(TypeError, match='attributes must be a list'):
            _summarize().plot(attributes='NDVI')

    def test_plot_aggregation_must_be_string(self):
        with pytest.raises(TypeError, match='aggregation must be a string'):
            _summarize().plot(attributes=['NDVI'], aggregation=['mean'])

    def test_plot_mean_std_rejects_unknown_option(self):
        with pytest.raises(ValueError, match='only "attribute" is available'):
            _summarize().plot_mean_std(aggregation='mean')

    def test_plot_mean_std_attribute_must_be_string(self):
        with pytest.raises(TypeError, match='attribute must be a string'):
            _summarize().plot_mean_std(attribute=123)
