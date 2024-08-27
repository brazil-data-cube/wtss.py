#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2024 INPE.
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

import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy
import shapely.geometry

from .summarize import Summarize
from .utils import render_html

Series = Dict[str, List[Union[float, str]]]
"""Represent the time series context attributes.

The keys available are:
- ``timeline``: List of given location series.
- ``values``: The map attributes and time series."""


@dataclass
class Location:
    """Represent the time series location.

    Once time series request is made in :class:`wtss.coverage.Coverage`, the location is created
    and related with time series attributes and values found for location.
    These values may be dynamically set using pagination.
    """

    geom: shapely.geometry.Point
    series: Series
    pixel_size: Tuple[float, float]

    @classmethod
    def from_dict(cls, pixel_center: Any, pixel_size: Any, time_series: Series):
        """Create a WTSS Location from dict keys found in Time Series result."""
        geom = shapely.geometry.shape(pixel_center)
        return cls(geom, time_series, pixel_size=pixel_size)

    @property
    def x(self):
        """Retrieve location longitude."""
        return self.geom.x

    @property
    def y(self):
        """Retrieve location latitude."""
        return self.geom.y

    @property
    def timeline(self) -> List[str]:
        """Retrieve the location time series associated."""
        return self.series['timeline']

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
        self._pagination = None
        if data.get('pagination'):
            self._pagination = data['pagination']

        self._locations = {}
        for location_ts in data['results']:
            location = Location.from_dict(**location_ts)
            self._locations[(location.x, location.y)] = location

    @property
    def total_locations(self):
        """Return the computed locations in timeseries."""
        return len(self._data['results'])

    @property
    def timeline(self):
        """Return the timeline associated to the time series."""
        return self._data['results'][0]['time_series']['timeline'] if len(self._data["results"]) > 0 else []

    @property
    def attributes(self):
        """Return a list with attribute names selected by user."""
        return [attr for attr in self._data['query']['attributes']]

    def values(self, attr_name) -> List[List[float]]:
        """Return the time series for the given attribute."""
        entries = [
            location.series['values'][attr_name] for location in self._locations.values()
        ]

        return entries

    @property
    def locations(self) -> dict:
        """Retrieve the time series locations matched as dict.

        Each location is a shapely.geometry.Point representing the pixel center.
        """
        return self._locations

    def summarize(self,
                  operations: Optional[List[str]] = None,
                  masked: Optional[bool] = False,
                  mask: Any = None,
                  start_datetime: Optional[str] = None,
                  end_datetime: Optional[str] = None) -> Summarize:
        """Summarize the current Time Series object."""
        if not start_datetime and not end_datetime:
            start_datetime = self._data['query']['start_datetime']
            end_datetime = self._data['query']['end_datetime']
            if self._pagination:
                start_datetime = self._pagination['start_datetime']
                end_datetime = self._pagination['end_datetime']

        return self._coverage.summarize(operations=operations,
                                        masked=masked,
                                        mask=mask,
                                        geom=self._data['query']['geom'],
                                        start_datetime=start_datetime,
                                        end_datetime=end_datetime,
                                        attributes=self._data['query']['attributes'])

    def plot(self, stats: bool = True, limit: Optional[int] = None, **options):
        """Plot the time series on a chart.

        Args:
            stats (bool): Flag to display time series statistics. Default is True.
                (Only applied on Time Series per Area)
            limit (Optiona[int]): Limit the number of time series to plot. Default is None.
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

        # Get attribute value if user defined, otherwise use the first
        attributes = options.get('attributes') or self.attributes

        axes = options.get("axes")
        fig = options.get("fig")

        if fig is None or axes is None:
            fig, axes = plt.subplots(len(attributes), figsize=(16, 5*len(attributes)))
            # fig, axes = plt.subplots(len(attributes), figsize=plt.figaspect(0.5))

            if len(attributes) == 1:
                axes = [axes]

        x = [dt.datetime.fromisoformat(d.replace('Z', '+00:00')) for d in self.timeline]

        attribute_map = {
            attr['name']: attr
            for attr in self._coverage.attributes
        }

        locations = list(self._locations.values())

        summarize_kwargs = {}
        if locations:
            summarize_kwargs["start_datetime"] = locations[0].timeline[0]
            summarize_kwargs["end_datetime"] = locations[0].timeline[-1]
        summarize = self.summarize(**summarize_kwargs)

        _limit = limit

        fig.show()

        for idx, axis in enumerate(axes):
            band_name = attributes[idx]
            attr_def = attribute_map[band_name]
            nodata = attr_def['nodata']

            if limit is None:
                _limit = len(self._locations)
            else:
                _limit = min(_limit, len(self.locations))

            alpha = 0.2 if _limit > 100 else 0.6

            for location in locations[:_limit]:
                values = [value if value != nodata else None for value in location.series['values'][band_name]]
                axis.plot(x, values, ls='-', linewidth=1, color='#7F9BB1', alpha=alpha)

            if stats:
                for quantile_name in ['q1', 'q3']:
                    quantile = numpy.ma.array(summarize.values(band_name).values(quantile_name))
                    quantile.mask = quantile == nodata
                    axis.plot(x, quantile.tolist(fill_value=None)[:len(x)], color='#b19541', linewidth=1.5)

                median = numpy.ma.array(summarize.values(band_name).values('median'))
                median.mask = median == nodata
                axis.plot(x, median.tolist(fill_value=None)[:len(x)], label=f'{band_name} median',
                          color='#B16240', linewidth=2.5)

            axis.text(-0.05, 0.5, f"{band_name}", transform=axis.transAxes, rotation=90, va='center', ha='left', fontsize=20) #Adjust subplot title position. Displacement ranges from 0 to 1. Negative to left and bottom, positive to right and up.
            fig.canvas.draw()

        title = 'Time Series'
        if _limit < len(self._locations):
            title += f' (Showing {_limit} of {len(self._locations)} points)'

        fig.suptitle(title, fontsize=22)

        fig.subplots_adjust(top=0.96) #Adjust distance the position of subplot border to figure border.

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
