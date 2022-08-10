#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to retrieve a time series."""

import os

from wtss import *

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)

service = WTSS('https://brazildatacube.dpi.inpe.br/dev/wtss/v2/', access_token=ACCESS_TOKEN)

print(service.coverages)
coverage = service['S2-SEN2COR_10_16D_STK-1']

timeseries = coverage.ts(attributes=['NDVI', 'EVI'],
                         geom={"type": "Polygon", "coordinates": [[[-55.46928, 1.47612], [-55.46928, 1.46612], [-55.45928, 1.46612], [-55.45928, 1.47612], [-55.46928, 1.47612]]]},
                         start_datetime='2017-01-01',
                         end_datetime='2020-12-31T23:59:00Z')

timeseries.plot()
