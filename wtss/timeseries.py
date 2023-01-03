#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a Time Series in WTSS."""

import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Union

import numpy
import shapely.geometry

from .summarize import Summarize
from .utils import render_html


Series = Dict[str, List[Union[float, str]]]
"""Represent the time series context attributes."""


@dataclass
class Location:
    """Represent the time series location.

    Once time series request is made in :class:`wtss.coverage.Coverage`, the location is created
    and related with time series attributes and values found for location.
    These values may be dynamically set using pagination.
    """
    geom: shapely.geometry.Point
    series: Series

    @classmethod
    def from_dict(cls, pixel_center: Any, time_series: Series):
        geom = shapely.geometry.shape(pixel_center)
        return cls(geom, time_series)

    @property
    def x(self):
        return self.geom.x

    @property
    def y(self):
        return self.geom.y

    def extend(self, other: 'Location'):
        """Extend time line values into current context."""
        other_timeline = other.series['timeline']
        other_series = other.series['values']

        self.series['timeline'].extend(other_timeline)
        for attribute, series in other_series.items():
            self.series['values'][attribute].extend(series)


class TimeSeries:
    """A class that represents a time series in WTSS.

    .. note::

        For more information about time series definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, coverage: 'Coverage', data, **options):
        """Create a TimeSeries object associated to a coverage.

        Args:
            coverage (Coverage): The coverage that this time series belongs to.
        """
        #: Coverage: The associated coverage.
        self._coverage = coverage
        self._options = options
        self._data = data

        self._pagination = {
            "pages": data['pagination']['total_pages'],
            "current": data['pagination']['page'],
            "next": data['pagination']['next'],
            "start_datetime": data['pagination']['start_datetime'],
            "end_datetime": data['pagination']['end_datetime']
        }

        self._locations = {}
        for location_ts in data['results']:
            location = Location.from_dict(**location_ts)
            self._locations[(location.x, location.y)] = location

    @property
    def success_query(self):
        """Verify if the query returned."""
        return True if len(self['results']) > 0 else False

    @property
    def total_locations(self):
        """Return the computed locations in timeseries."""
        return len(self._data['results'])

    @property
    def timeline(self):
        """Return the timeline associated to the time series."""
        return self._data['results'][0]['time_series']['timeline']

    @property
    def attributes(self):
        """Return a list with attribute names selected by user."""
        return [attr for attr in self._data['query']['attributes']]

    @property
    def attributes_objects(self):
        """Return a list with attributes objects."""
        return [attr_obj for attr_obj in self._coverage.attributes if attr_obj['name'] in self.attributes]

    def values(self, attr_name):
        """Return the time series for the given attribute."""
        return getattr(self, attr_name)

    def _next_time_series(self, page: int):
        return self._coverage.ts(params=dict(page=page), **self._options)

    def _time_series_it(self):
        for page in range(self._pagination['next'], self._pagination['pages']):
            ts = self._next_time_series(page)

            # Modify global ctx
            self._modify_ts_context(ts)

            yield self

    def _modify_ts_context(self, ts: 'TimeSeries'):
        for idx, location in ts.locations.items():
            self_location = self._locations[idx]

            self_location.extend(location)

        self._pagination['next'] = ts._pagination['next']

    def iterator(self, progress: bool = True) -> Iterator['TimeSeries']:
        import click

        with click.progressbar(self._time_series_it(),
                               length=self._pagination['pages']) as bar:
            for location in bar:
                yield location

    @property
    def locations(self) -> dict:
        """Iterator that yields location objects.

        Each location is a shapely.geometry.Point representing the pixel center.
        """
        return self._locations

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
        for attribute in self.attributes:
            for location in self._locations.values():
                series = location.series[attribute]
                values.append(series)

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
                                        geom=self._data['query']['geom'],
                                        start_datetime=self._data['query']['start_datetime'],
                                        end_datetime=self._data['query']['end_datetime'],
                                        attributes=self._data['query']['attributes'])

    def plot(self, stats: bool = True, plot=None, limit: int = 1000, **options):
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

        if limit is not None and limit < 0:
            raise ValueError('Limit cannot be negative')

        summarize = self.summarize()

        # Get attribute value if user defined, otherwise use the first
        attributes = options.get('attributes') or self.attributes

        # if plot is None:
        #     _ = plt.subplots(len(attributes), 1)

        axes = plt.gca()
        fig = plt.gcf()

        if len(attributes) == 1:  # For single attribute, transform into sequence to continue workflow
            axes = [axes]

        x = [dt.datetime.fromisoformat(d.replace('Z', '+00:00')) for d in self.timeline]
        xstats = sorted(list(set(x)))

        attribute_map = {
            attr['name']: attr
            for attr in self._coverage.attributes
        }

        for idx, axis in enumerate(axes):
            band_name = attributes[idx]
            attr_def = attribute_map[band_name]
            nodata = attr_def['nodata']

            _limit = limit
            if limit is None:
                _limit = len(self._locations)

            alpha = 0.2 if _limit > 100 else 0.6

            for location in list(self._locations.values())[:_limit]:
                values = [value if value != nodata else None for value in location.series['values'][band_name]]
                axis.plot(x, values, ls='-', linewidth=1, color='#7F9BB1', alpha=alpha)

            if stats:
                for quantile_name in ['q1', 'q3']:
                    quantile = numpy.ma.array(summarize.values(band_name).values(quantile_name))
                    quantile.mask = quantile == nodata
                    axis.plot(xstats, quantile.tolist(fill_value=None)[:len(x)], color='#b19541', linewidth=1.5)

                median = numpy.ma.array(summarize.values(band_name).values('median'))
                median.mask = median == nodata
                axis.plot(xstats, median.tolist(fill_value=None)[:len(x)], label=f'{band_name} median',
                          color='#B16240', linewidth=2.5)

            plt.draw()
            plt.pause(0.01)

        fig.autofmt_xdate()

    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints a time series."""
        return self._repr_html_()

    def _repr_html_(self):
        """Display the time series as a HTML.

        This integrates a rich display in IPython.
        """
        html = render_html('timeseries.html', timeseries=self)

        return html
