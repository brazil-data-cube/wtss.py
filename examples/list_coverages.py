#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows the available coverages in WTSS."""

from wtss import *
import os 

BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)
WTSS_SERVER_URL = os.getenv("WTSS_SERVER_URL", None)

service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)

print('\n cubes:')
print(service.cubes)

print('\n collections:')
print(service.collections)

print('\n classifications:')
print(service.classifications)

print('\n mosaics:')
print(service.mosaics)