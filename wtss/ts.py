#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to retrieve and plot a time series."""

from wtss import *

service = WTSS(url='http://127.0.0.1:6000', access_token='TfQ9LCjX0Koate0zZi2U9xVwYux97JRy7f6gwNJjZF')

coverage = service['MOD13Q1-6']

ts = coverage.ts(attributes = ['NDVI','EVI'],
                 geom = {"type":"Polygon","coordinates":[[[-52.79548645019531,-28.29304474924502],[-52.780723571777344,-28.29304474924502],[-52.780723571777344,-28.283068128797773],[-52.79548645019531,-28.283068128797773],[-52.79548645019531,-28.29304474924502]]]},
                 start_datetime = '2017-01-01T00:00:00Z', 
                 end_datetime = '2017-02-01T00:00:00Z')

print(ts.NDVI)
print(ts.EVI)
print(ts.timeline)

# ts.plot(attributes=['NDVI'])