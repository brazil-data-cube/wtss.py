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

"""Offline tests for the ``wtss`` command-line interface."""

import responses
from click.testing import CliRunner

from test_mock import (MOCK_URL, _register_coverage, _register_root,
                       _register_timeseries)
from wtss.cli import cli


class TestTs:
    """``wtss ts`` must retrieve and print a time series end-to-end.

    Regression for B21 (a second CLI bug beyond B3): the command accessed
    ``.attributes`` on the deferred ``TimeSeriesSearch`` instead of on the
    parsed ``TimeSeries`` (``search.ts``), raising AttributeError on every run.
    """

    @responses.activate
    def test_ts_runs_and_prints_series(self):
        _register_root(responses.mock)
        _register_coverage(responses.mock)
        _register_timeseries(responses.mock)
        runner = CliRunner()
        result = runner.invoke(cli, [
            'ts', '-u', MOCK_URL, '-c', 'MOD13Q1-6', '-a', 'NDVI',
            '--latitude', '-12', '--longitude', '-54',
            '--start-datetime', '2017-01-01', '--end-datetime', '2017-02-28',
        ])
        assert result.exit_code == 0, result.output
        assert 'NDVI' in result.output
        assert 'timeline' in result.output
