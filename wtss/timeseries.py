#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a Time Series in WTSS."""


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

    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints a time series."""
        return 'TimeSeries:'


    def _repr_html_(self):
        """Display the time series as a HTML.

        This integrates a rich display in IPython.
        """
        return '<h1>TimeSeries:</h1>'
