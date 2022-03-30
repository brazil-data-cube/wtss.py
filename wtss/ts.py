#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to retrieve a time series and a summarized time series."""

from wtss import *
import os 

BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)
WTSS_SERVER_URL = os.getenv("WTSS_SERVER_URL", None)

service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)

print('cubes:', service.cubes)
print('collections:', service.collections)
print('classifications:', service.classifications)
print('mosaics', service.mosaics)

coverage = service['MOD13Q1-6']

# Set geometry (geom can be a GeoJSON, a string or a shapely geometry)
geom_json = {"type":"Polygon","coordinates":[[[-54,-12],[-53.99,-12],[-53.99,-11.99],[-54,-11.99],[-54,-12]]]}
geom_json = {"type":"Point","coordinates":[-54,-12]}
geom_str = '{"type":"Polygon","coordinates":[[[-54,-12],[-53.99,-12],[-53.99,-11.99],[-54,-11.99],[-54,-12]]]}'
import shapely.geometry
geom_shapely = shapely.geometry.shape(geom_json)


# Invokes timeseries functionality
timeseries = coverage.ts(attributes = ['NDVI','EVI'],
                        geom = geom_json,
                        #  longitude = -54,
                        #  latitude = -12,
                        start_datetime = '2017-01-01',
                        end_datetime = '2017-02-01')

print(timeseries.success_request)
print(timeseries.number_of_pixels)
print(timeseries.NDVI)
print(timeseries.EVI)
print(timeseries.timeline)


# Invokes summarize functionality
summarize = coverage.summarize( attributes = ['NDVI','EVI'],
                                # geom = geom_str,
                                longitude = -54,
                                latitude = -12,
                                start_datetime = '2017-01-01', 
                                end_datetime = '2017-02-01T00:00:00Z',
                                applyAttributeScale = False)

print(summarize.success_request)
print(summarize.NDVI['mean'])
print(summarize.EVI['median'])
print(summarize.timeline)