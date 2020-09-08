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

    def plot(self):
        """Plot the time series on a chart.

        .. note::

            You should have Matplotlib and Numpy installed.
            See ``wtss.py`` install notes for more information.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except:
            raise ImportError('You should install Matplotlib and Numpy!')

        fig, ax = plt.subplots()

        plt.title(f'Coverage {self._coverage["name"]}', fontsize=24)

        plt.xlabel('Date', fontsize=16)
        plt.ylabel('Surface Reflectance', fontsize=16)

        x = [str(date) for date in self.timeline]

        plt.xticks(np.linspace(0, len(x), num=10))

        attrs = self['result']['attributes']

        for attr in attrs:
            attr_name = attr['attribute']

            y = attr['values']

            ax.plot(x, y,
                    ls='-',
                    marker='o',
                    linewidth=1.0,
                    label=attr_name)

        plt.legend()

        plt.grid(b=True, color='gray', linestyle='--', linewidth=0.5)

        fig.autofmt_xdate()

        plt.show()


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