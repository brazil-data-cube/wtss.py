#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
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
    
    def values(self, attr_name):
        """Return the time series for the given attribute."""
        return getattr(self, attr_name)


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
    def geometry(self):
        """Return the geometry used to query."""
        return self['query']['geom']


    @property
    def success_request(self):
        """Return a list with attribute names."""
        return True if len(self['results']['values'])>0 else False


    def values(self, attr_name):
        """Return the time series for the given attribute."""
        return getattr(self, attr_name)


    def pandas_dataframe(self, **options):
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
        except:
            raise ImportError('Cannot import one of the following libraries: [pandas, matplotlib].')

        # Build the dataframe in a tibble format
        attrs = []
        aggrs = []
        datetimes = []
        values = []
        for attr_name in self.attributes:
            for i in range(0, len(self.timeline)):
                for aggr_name in ['min','max','mean','median','std']:
                    datetimes.append(self.timeline[i])
                    attrs.append(attr_name)
                    aggrs.append(aggr_name)
                    values.append(self.values(attr_name).values(aggr_name)[i])

        df = pd.DataFrame({
            'attribute': attrs,
            'aggregation': aggrs,
            'datetime': pd.to_datetime(datetimes, format="%Y-%m-%dT%H:%M:%SZ", errors='ignore'),
            'value': values,
        })
        
        return df


    
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

        .. note::
            You should have Matplotlib and Numpy installed.
            See :ref:`wtss.py install notes <Installation>` for more information.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import datetime as dt
        except:
            raise ImportError('Could not import some of the packages [matplotlib, numpy, datetime].')

        fig, ax = plt.subplots()
        plt.title(f'{self._coverage.name}', fontsize=20)
        plt.xlabel('Date', fontsize=16)
        plt.ylabel('Value', fontsize=16)

        x = self.timeline
        x = [dt.datetime.strptime(d, '%Y-%m-%dT%H:%M:%SZ').date() for d in self.timeline]

        attributes = options['attributes'] if 'attributes' in options else self.attributes
        aggregation = options['aggregation'] if 'aggregation' in options else 'mean'

        for attr in attributes:
            y = self.values(attr).values(aggregation)
            ax.plot(x, y, ls='-', linewidth=1.5, label=attr)

        plt.legend()
        plt.grid(b=True, color='gray', linestyle='--', linewidth=0.5)

        fig.autofmt_xdate()
        plt.show()


    def plot_mean_std(self, **options):
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import datetime as dt
        except:
            raise ImportError('Could not import some of the packages [matplotlib, numpy, datetime].')

        fig, ax = plt.subplots()
        plt.title(f'{self._coverage.name}', fontsize=20)
        plt.xlabel('Date', fontsize=16)
        plt.ylabel('Value', fontsize=16)

        x = self.timeline
        x = [dt.datetime.strptime(d, '%Y-%m-%dT%H:%M:%SZ').date() for d in self.timeline]

        attribute = options['attribute'] if 'attribute' in options else self.attributes

        mean = self.values(attribute).values('mean')
        std = self.values(attribute).values('std')
        mean_add_std = sum = [x+y for (x,y) in zip(mean, std)]
        mean_sub_std = sum = [x-y for (x,y) in zip(mean, std)]

        ax.plot(x, mean, ls='-', linewidth=1.5, label='mean', color='darkgreen')
        ax.plot(x, mean_add_std, ls='--', linewidth=1, label='mean + std', color='red')
        ax.plot(x, mean_sub_std, ls='--', linewidth=1, label='mean - std', color='red')

        plt.legend()

        fig.autofmt_xdate()
        plt.show()


    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints a time series."""
        return self._repr_html_()


    def _repr_html_(self):
        """Display the summarized time series as a HTML.

        This integrates a rich display in IPython.
        """
        html = render_html('summarize.html', summarize=self)

        return html