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

"""Unit-test configuration for the WTSS Python Client Library for."""

import json
import os

import pkg_resources
import pytest


@pytest.fixture
def URL():
    """Return the WTSS URL to be used in tests."""
    return os.getenv('WTSS_TEST_URL', 'http://localhost')


@pytest.fixture
def ListCoverageResponse():
    """Return the list of coverages to be validated."""
    resource_package = __name__
    doc = pkg_resources.resource_string(resource_package,
                                        'json/list_coverages_response.json')

    return json.loads(doc)


@pytest.fixture
def MOD13Q1():
    """Return the MOD13Q1 metadata."""
    resource_package = __name__
    doc = pkg_resources.resource_string(resource_package,
                                        'json/describe_coverage_response.json')

    return json.loads(doc)