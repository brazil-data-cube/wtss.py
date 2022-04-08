#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to retrieve a summarized time series.

Aggregation methods available are min, max, mean, median and std.
"""
import os

from wtss import *

BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)
WTSS_SERVER_URL = os.getenv("WTSS_SERVER_URL", None)

service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)

coverage = service['MOD13Q1-6']
print(coverage.attributes)

summarize = coverage.summarize( attributes = ['NDVI','EVI'],
                                geom = {"type":"Polygon","coordinates":[[[-54,-12],[-53.99,-12],[-53.99,-11.99],[-54,-11.99],[-54,-12]]]},
                                start_datetime = '2017-01-01', 
                                end_datetime = '2018-02-01',
                                applyAttributeScale = False)

print('\nNDVI mean:', summarize.NDVI.mean)
print('\EVI std:', summarize.EVI.std)
print('\ntimeline:', summarize.timeline)

summarize.plot_mean_std(attribute='NDVI')