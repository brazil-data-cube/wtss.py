#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to traverse the list of coverages in a service."""

from wtss import *

service = WTSS('http://www.esensing.dpi.inpe.br')

for cv in service:
    print(cv)