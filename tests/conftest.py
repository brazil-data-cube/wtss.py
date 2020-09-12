#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
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