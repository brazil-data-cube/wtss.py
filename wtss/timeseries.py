#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a Time Series in WTSS."""

import datetime as dt
from typing import Any, Iterator, List, Optional

import numpy
import shapely.geometry

from .summarize import Summarize
from .utils import render_html


class TimeSeries(dict):
    """A class that represents a time series in WTSS.

    .. note::

        For more information about time series definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, coverage: 'Coverage', data):
        """Create a TimeSeries object associated to a coverage.

        Args:
            coverage (Coverage): The coverage that this time series belongs to.
        """
        #: Coverage: The associated coverage.
        self._coverage = coverage

        setattr(self, 'query', data['query'])

        super(TimeSeries, self).__init__(data or {})

        # Add all timeseries from an attribute as object property
        if self.success_query:
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
    def success_query(self):
        """Verify if the query returned."""
        return True if len(self['results']) > 0 else False

    @property
    def total_locations(self):
        """Return the computed locations in timeseries."""
        return len(self['results'])

    @property
    def timeline(self):
        """Return the timeline associated to the time series."""
        return self['results'][0]['time_series']['timeline'] if self.success_query else None

    @property
    def attributes(self):
        """Return a list with attribute names selected by user."""
        return [attr for attr in self['results'][0]['time_series']['values']] if self.success_query else None

    @property
    def attributes_objects(self):
        """Return a list with attributes objects."""
        return [attr_obj for attr_obj in self._coverage.attributes if attr_obj['name'] in self.attributes]

    def values(self, attr_name):
        """Return the time series for the given attribute."""
        return getattr(self, attr_name)

    @property
    def locations(self) -> Iterator[shapely.geometry.Point]:
        """Iterator that yields location objects.

        Each location is a shapely.geometry.Point representing the pixel center.
        """
        return map(lambda location: shapely.geometry.shape(location['pixel_center']), self['results'])

    def df(self):
        """Create a pandas dataframe with timeseries data.

        Raises:
            ImportError: If pandas or matplotlib could not be imported.
        """
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
        except:
            raise ImportError('Cannot import one of the following libraries: [pandas, matplotlib].')

        # Build the dataframe in a tibble format
        attrs = []
        datetimes = []
        pixels_ids = []
        values = []
        for attr_name in self.attributes:
            for pixel_id in range(0, len(self.values(attr_name))):
                pixel_timeserie = self.values(attr_name)[pixel_id]
                for i in range(0, len(self.timeline)):
                    attrs.append(attr_name)
                    pixels_ids.append(pixel_id)
                    datetimes.append(self.timeline[i])
                    values.append(pixel_timeserie[i])

        df = pd.DataFrame({
            'attribute': attrs,
            'pixel_id': pixels_ids,
            'datetime': pd.to_datetime(datetimes, format="%Y-%m-%dT%H:%M:%SZ", errors='ignore'),
            'value': values,
        })
        
        return df

    def summarize(self,
                  operations: Optional[List[str]] = None,
                  masked: Optional[bool] = False,
                  mask: Any = None) -> Summarize:
        """Summarize the current Time Series object."""
        return self._coverage.summarize(operations=operations,
                                        masked=masked,
                                        mask=mask,
                                        geom=self['query']['geom'],
                                        start_datetime=self['query']['start_datetime'],
                                        end_datetime=self['query']['end_datetime'],
                                        attributes=self['query']['attributes'])

    def plot(self, stats: bool = True, limit: int = 1000, **options):
        """Plot the time series on a chart.

        Args:
            stats (bool): Flag to display time series statistics. Default is True.
                (Only applied on Time Series per Area)
            limit (int): Limit the number of time series to plot. Default is 1000.
                When None, display all. You may have performance issues.

        Keyword Args:
            attributes (sequence): A sequence like ('red', 'nir') or ['red', 'nir'] .
            line_styles (sequence): Not implemented yet.
            markers (sequence): Not implemented yet.
            line_width (numeric): Not implemented yet.
            line_widths (sequence): Not implemented yet,
            labels (sequence): Not implemented yet.
        Raises:
            ImportError: If datetime, matplotlib or numpy or datetime could not be imported.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError('You should install Matplotlib and Numpy!')

        summarize = self.summarize()

        # Get attribute value if user defined, otherwise use the first
        attributes = options.get('attributes') or self.attributes

        # Create plot
        fig, axes = plt.subplots(len(attributes), 1)

        if len(attributes) == 1:  # For single attribute, transform into sequence to continue workflow
            axes = [axes]

        x = [dt.datetime.fromisoformat(d.replace('Z', '+00:00')) for d in self.timeline]

        attribute_map = {
            attr['name']: attr
            for attr in self._coverage.attributes
        }

        for idx, axis in enumerate(axes):
            band_name = attributes[idx]
            ts = self.values(band_name)
            attr_def = attribute_map[band_name]
            nodata = attr_def['nodata']

            _limit = limit
            if limit is None:
                _limit = len(ts)

            for pixel_ts in ts[:_limit]:
                pixel_ts = [v if v != nodata else None for v in pixel_ts]
                axis.plot(x, pixel_ts, ls='-', linewidth=1, color='#7F9BB1', alpha=0.2)

            if stats:
                for quantile_name in ['q1', 'q3']:
                    quantile = numpy.ma.array(summarize.values(band_name).values(quantile_name))
                    quantile.mask = quantile == nodata
                    axis.plot(x, quantile.tolist(fill_value=None), color='#b19541', linewidth=1.5)

                median = numpy.ma.array(summarize.values(band_name).values('median'))
                median.mask = median == nodata
                axis.plot(x, median.tolist(fill_value=None), label=f'{band_name} median',
                          color='#B16240', linewidth=2.5)

            axis.grid(b=True, color='gray', linestyle='--', linewidth=0.5)
            axis.legend()
            axis.set_ylabel(band_name)

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
