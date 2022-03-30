#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a Time Series in WTSS."""

from utils import render_html


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

        # # add coverage attributes as object keys
        # if len(self['results']) > 0:
        #     attributes = [attr_result for attr_result in self['results'][0]['time_series']['values'].items()]
        #     for attr_name, aggr_results in attributes:
        #         setattr(self, attr_name, aggr_results)

        # if len(self['results']) > 0:
        #     attributes = [attr_result for attr_result in self['results'][0]['time_series']['values'].items()]
        #     values = dict()
        #     for attr_name, values0 in attributes:
        #         values[attr_name] = values0
        #     for i in range(0, len(self['results'])):
        #         attributes = [attr_result for attr_result in self['results'][i]['time_series']['values'].items()]
            
        #     for i in range(0, len(self['results'])):
        #         attributes = [attr_result for attr_result in self['results'][i]['time_series']['values'].items()]
        #     for attr_name, aggr_results in attributes:
        #         setattr(self, attr_name, aggr_results)



        if len(self['results']) > 0:
            # Get attribute names and first timeseries
            values = dict()
            attributes = [attrs for attrs in self['results'][0]['time_series']['values'].items()]
            for attr_name, values0 in attributes:
                values[attr_name] = [values0]
            # Get remaining timeseries
            for i in range(1, len(self['results'])):
                attributes = [attrs for attrs in self['results'][i]['time_series']['values'].items()]
                for attr_name, timeserie in attributes:
                    values[attr_name].append(timeserie)
            # Create self attributes with the results
            for attr_name, all_timeseries in values.items():
                setattr(self, attr_name, all_timeseries)

    @property
    def number_of_pixels(self):
        """Return the number of pixels computed in timeseries."""
        return len(self['results'])

    @property
    def timeline(self):
        """Return the timeline associated to the time series."""
        return self['results'][0]['time_series']['timeline'] if len(self['results'])>0 else None


    @property
    def success_request(self):
        """Return a list with attribute names."""
        return True if len(self['results'])>0 else False
        

    @property
    def attributes(self):
        """Return a list with attribute names."""
        return [attr for attr in self['results'][0]['time_series']['values']] if len(self['results'])>0 else None


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