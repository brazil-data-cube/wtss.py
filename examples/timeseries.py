#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
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