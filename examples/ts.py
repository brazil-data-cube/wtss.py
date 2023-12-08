#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to retrieve a time series."""

import os

import shapely.geometry

from wtss import *

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)

service = WTSS('https://brazildatacube.dpi.inpe.br/dev/wtss/v2/', access_token=ACCESS_TOKEN)

print(service.coverages)
coverage = service['S2-16D-2']

timeseries = coverage.ts(attributes=('NDVI',),
                         geom=shapely.geometry.box(-59.60, -5.69, -59.59, -5.68),
                         start_datetime="2020-01-01", end_datetime="2022-12-31")

# Show total of locations matched
total = timeseries.total_locations()
print(total)

# You can plot all once
timeseries.plot(paginate=True)

# Create GeoPandas DataFrame of Series
df = timeseries.df()
print(df)
