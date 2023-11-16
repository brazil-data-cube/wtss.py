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
"""A class that represents a Time Series in WTSS."""

from .utils import render_html


class TimeSeries(dict):
    """A class that represents a time series in WTSS.

    .. note::

        For more information about time series definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, coverage, data):
        """Create a TimeSeries object associated to a coverage.

        Args:
            coverage (Coverage): The coverage that this time series belongs to.
        """
        #: Coverage: The associated coverage.
        self._coverage = coverage

        super(TimeSeries, self).__init__(data or {})

        # add coverage attributes as object keys
        attrs = self['result']['attributes']

        for attr in attrs:
            setattr(self, attr['attribute'], attr['values'])


    @property
    def timeline(self, as_date=False, fmt=''):
        """Return the timeline associated to the time series."""
        return self['result']['timeline']


    @property
    def attributes(self):
        """Return a list with attribute names."""
        attributes = [attr['attribute'] for attr in self['result']['attributes']]

        return attributes


    def values(self, attr_name):
        """Return the time series for the given attribute."""
        return getattr(self, attr_name)


    def plot(self, **options):
        """Plot the time series on a chart.

        Keyword Args:
            attributes (sequence): A sequence like ('red', 'nir') or ['red', 'nir'] .
            line_styles (sequence): Not implemented yet.
            markers (sequence): Not implemented yet.
            line_width (numeric): Not implemented yet.
            line_widths (sequence): Not implemented yet,
            labels (sequence): Not implemented yet.

        Raises:
            ImportError: If Maptplotlib or Numpy can no be imported.

        Example:

            Plot the time series of MODIS13Q1 data product:

            .. doctest::
                :skipif: True

                >>> from wtss import *
                >>> service = WTSS(WTSS_EXAMPLE_URL)
                >>> coverage = service['MOD13Q1']
                >>> ts = coverage.ts(attributes=('red', 'nir'),
                ...                  latitude=-12.0, longitude=-54.0,
                ...                  start_date='2001-01-01', end_date='2001-12-31')
                ...
                >>> ts.plot()

            This will produce the following time series plot:

            .. image:: ./img/ts_plot.png
                :alt: Time Series
                :width: 640px

        .. note::

            You should have Matplotlib and Numpy installed.
            See :ref:`wtss.py install notes <Installation>` for more information.
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

        x = self.timeline

        plt.xticks(np.linspace(0, len(x), num=10))

        attrs = options['attributes'] if 'attributes' in options else self.attributes

        for attr in attrs:
            y = self.values(attr)

            ax.plot(x, y,
                    ls='-',
                    marker='o',
                    linewidth=1.0,
                    label=attr)

        plt.legend()

        plt.grid(visible=True, color='gray', linestyle='--', linewidth=0.5)

        fig.autofmt_xdate()

        plt.show()


    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints a time series."""
        return self._repr_html_()


    def _repr_html_(self):
        """Display the time series as a HTML.

        This integrates a rich display in IPython.
        """
        html = render_html('timeseries.html', timeseries=self)

        return html