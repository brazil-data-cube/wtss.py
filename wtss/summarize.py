#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a Time Series in WTSS."""

from pystac import Summaries
from .utils import render_html


class SummarizeAttributeResult:
    """A class that represents a summarized attribute."""

    def __init__(self, aggr_results:dict):
        for aggr_name, aggr_result in aggr_results:
            setattr(self, aggr_name, aggr_result)


class Summarize(dict):
    """A class that represents a summarized timeseries in WTSS.

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

        super(Summarize, self).__init__(data or {})

        # add coverage attributes as object keys
        if len(self['results']['values']) > 0:
            attributes = [attr_result for attr_result in self['results']['values'].items()]
            # For each attribute, create a property
            for attr_name, aggr_results in attributes:
                setattr(self, attr_name, SummarizeAttributeResult( aggr_results.items() ))


    @property
    def timeline(self, as_date=False, fmt=''):
        """Return the timeline associated to the time series."""
        return self['results']['timeline'] if len(self['results']['timeline'])>0 else None


    @property
    def attributes(self):
        """Return a list with attribute names."""
        return [attr for attr in self['results']['values'].keys()] if len(self['results']['values'])>0 else None


    @property
    def success_request(self):
        """Return a list with attribute names."""
        return True if len(self['results']['values'])>0 else False


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
                ...                  start_datetime='2001-01-01', end_datetime='2001-12-31')
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

        plt.grid(b=True, color='gray', linestyle='--', linewidth=0.5)

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