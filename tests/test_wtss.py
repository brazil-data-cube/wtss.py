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

import pytest
from requests import ConnectionError as _ConnectionError

from wtss import *


@pytest.mark.xfail(raises=_ConnectionError,
                    reason='WTSS server not reached!')
def test_list_coverages(URL, ListCoverageResponse):
    service = WTSS(URL)

    assert set(service.coverages) == set(ListCoverageResponse['coverages'])


@pytest.mark.xfail(raises=_ConnectionError,
                    reason='WTSS server not reached!')
def test_describe_coverage(URL, MOD13Q1):
    service = WTSS(URL)

    cov = service['MOD13Q1']

    assert cov.name == MOD13Q1['name']
    assert cov.spatial_extent == MOD13Q1['spatial_extent']
    assert cov.spatial_resolution == MOD13Q1['spatial_resolution']
    assert cov.attributes == MOD13Q1['attributes']


@pytest.mark.xfail(raises=_ConnectionError,
                   reason='WTSS server not reached!')
@pytest.mark.parametrize(
    'coverage, attr, location, start_date, end_date, result',
    [
        ('MOD13Q1', 'nir', dict(latitude=-12, longitude=-54),
         '2001-01-01', '2001-12-31',
         [
             3463.0, 3656.0, 2883.0, 4130.0, 2910.0, 3300.0,
             3281.0, 2979.0, 2953.0, 2876.0, 2872.0, 2854.0,
             2977.0, 3008.0, 3040.0, 3201.0, 3297.0, 2815.0,
             3546.0, 4161.0, 4097.0, 3901.0, 2948.0
         ])
    ]
)
def test_st(URL, coverage, attr, location, start_date, end_date, result):
    service = WTSS(URL)

    cov = service[coverage]

    ts = cov.ts(attributes=attr,
                latitude=location['latitude'], longitude=location['longitude'],
                start_date=start_date, end_date=end_date)

    assert ts.values(attr) == result