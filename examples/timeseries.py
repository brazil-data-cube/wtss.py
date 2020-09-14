#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to retrieve and plot a time series."""

from wtss import *

service = WTSS('http://www.esensing.dpi.inpe.br')

coverage = service['MOD13Q1']

ts = coverage.ts(attributes=('red', 'nir', 'blue'),
                 latitude=-12.0, longitude=-54.0,
                 start_date='2001-01-01', end_date='2001-12-31')

print(ts.red)

print(ts.nir)

print(ts.timeline)

ts.plot(attributes=['blue'])