#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Python Client Library for WTSS."""

from .wtss import wtss
from .version import __version__

__all__ = (
    '__version__',
    'wtss',
)
