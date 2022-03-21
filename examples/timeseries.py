#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020-2021 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to retrieve and plot a time series."""

from wtss import *

service = WTSS('https://brazildatacube.dpi.inpe.br/', access_token='change-me')

coverage = service['MOD13Q1-6']

ts = coverage.ts(attributes=('red_reflectance', 'NIR_reflectance', 'blue_reflectance'),
                 latitude=-12.0, longitude=-54.0,
                 start_date='2001-01-01', end_date='2001-12-31')

print(ts.red_reflectance)

print(ts.NIR_reflectance)

print(ts.timeline)

ts.plot(attributes=['blue_reflectance'])