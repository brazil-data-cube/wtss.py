#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit-test for the WTSS Python Client Library for."""

from wtss import *


def test_list_coverages(URL, ListCoverageResponse):
    service = WTSS(URL)

    assert set(service.coverages) == set(ListCoverageResponse['coverages'])


def test_list_coverages(URL, MOD13Q1):
    service = WTSS(URL)

    cov = service['MOD13Q1']

    assert cov.name == MOD13Q1['name']
    assert cov.spatial_extent == MOD13Q1['spatial_extent']
    assert cov.spatial_resolution == MOD13Q1['spatial_resolution']
    assert cov.attributes == MOD13Q1['attributes']
