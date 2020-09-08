#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a Time Series in WTSS."""

from datetime import datetime


class TimeSeries(dict):
    """A class that represents a time series in WTSS.

    For more information about time series definition in WTSS, please,
     refer to the `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.

    Attributes:

        _coverage (Coverage): The associated coverage.
    """

    def __init__(self, coverage, data):
        """Create a TimeSeries object associated to a coverage.

        Args:
            coverage (Coverage): The coverage that this time series belongs to.
        """
        self._coverage = coverage

        super(TimeSeries, self).__init__(data or {})

        # update timeline with datetime type
        tl = data["result"]["timeline"]

        self['result']['timeline'] =  self._timeline(tl, '%Y-%m-%d')

        # add coverage attributes in object keys
        attrs = self['result']['attributes']

        for attr in attrs:
            setattr(self, attr['attribute'], attr['values'])


    @property
    def timeline(self):
        return self['result']['timeline']


    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints a time series."""
        return 'TimeSeries:'


    def _repr_html_(self):
        """Display the time series as a HTML.

        This integrates a rich display in IPython.
        """
        return '<h1>TimeSeries:</h1>'


    @staticmethod
    def _timeline(tl, fmt):
        """Convert a timeline from a string list to a Python datetime list.

        Args:
            tl (list): a list of strings from a time_series JSON document response.
            fmt (str): the format date (e.g. `"%Y-%m-%d`").

        Returns:
            list (datetime): a timeline with datetime values.
        """
        date_timeline = [datetime.strptime(t, fmt).date() for t in tl]

        return date_timeline