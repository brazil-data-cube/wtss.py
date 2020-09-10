#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Utility functions for WTSS client library."""

from datetime import datetime


def to_datetime(timeline, fmt='%Y-%m-%d'):
    """Convert a timeline from a string list to a Python datetime list.

    Args:
        timeline (list): a list of strings representing dates.
        fmt (str): the format date (e.g. `"%Y-%m-%d`").

    Returns:
        list (datetime): a timeline with datetime values.
    """
    date_timeline = [datetime.strptime(t, fmt).date() for t in timeline]

    return date_timeline