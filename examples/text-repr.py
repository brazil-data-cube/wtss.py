#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020-2021 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how the various text representation for services and coverages."""

from wtss import *

service = WTSS('https://brazildatacube.dpi.inpe.br/dev', access_token='change-me')

print(service)
print(str(service))
print(repr(service))
print(service._repr_html_())


print(service['CB4_64_16D_STK-1'])
print(str(service['CB4_64_16D_STK-1']))
print(repr(service['CB4_64_16D_STK-1']))
print(service['CB4_64_16D_STK-1']._repr_html_())

ts = service.MOD13Q1.ts(attributes='red, nir',
                        latitude=-12, longitude=-54,
                        start_date='2001-01-01', end_date='2001-12-31')
print(ts)
print(str(ts))
print(repr(ts))
print(ts._repr_html_())
