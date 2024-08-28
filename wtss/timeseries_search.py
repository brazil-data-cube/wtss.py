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

"""Represent the module that defers a query to WTSS Time series endpoint a Time Series in WTSS."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Iterator, List, Optional

import shapely
from geopandas import GeoDataFrame

from .summarize import Summarize
from .timeseries import TimeSeries


@dataclass(frozen=True)
class TimeSeriesQuery:
    """Represent the Web Time Series query parameters.

    These values are in conformance of WTSS time series endpoint as described in the
    `WTSS API - Time Series spec <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    params: Any
    """Define the parameters used on GET."""
    attributes: List[str]
    """Define the list of attributes to retrieve time series."""
    start_datetime: Optional[str]
    """The start datetime offset for series."""
    end_datetime: Optional[str]
    """The end datetime offset for series."""
    geom: shapely.geometry.base.BaseGeometry
    """The geometry used to retrieve time series."""
    pagination: Optional[str] = field(default='P3M')
    """The paginator factor used in time series. Defaults to ``P3M``,
    which means periods of 3 months.

    Follows ISO 8601 Temporal Duration.
    """


@dataclass()
class TimeSeriesSearch:
    """Represent a deferred query to WTSS Time series endpoint.

    No request is sent to API until a method is called to iterate
    through the resulting time series iterator. This feature
    can be achieved using :meth:`TimeSeriesSearch.iterator` or
    :meth:`TimeSeriesSearch.df`.

    This interface also support the way to represent time series
    using `geopandas.GeoDataFrame <https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html>`_
    as described below::

        import shapely.geometry
        from wtss import WTSS

        service = WTSS('https://brazildatacube.dpi.inpe.br/dev/wtss/v2/', access_token='<personal-token>')
        coverage = service['S2-16D-2']
        timeseries = coverage.ts(attributes=('NDVI',),
                                 geom=shapely.geometry.MultiPoint([
                                    shapely.geometry.Point(-59.60, -5.69),
                                    shapely.geometry.Point(-59.59, -5.69),
                                    shapely.geometry.Point(-59.58, -5.69),
                                 ]),
                                 start_datetime="2020-01-01", end_datetime="2022-12-31"

        df = timeseries.df()
        print(df.head())

    You can also plot the time series using builtin :meth:`TimeSeriesSearch.plot` as following::

        timeseries.plot()

    Args:
        coverage: The coverage instance :class:`wtss.coverage.Coverage`.
        query: The query filter for time series
    """

    coverage: 'Coverage'
    query: TimeSeriesQuery
    _pagination: Optional[Any] = None
    _ts: Optional[TimeSeries] = None
    """Context reference for Time Series.

    The locations time series are used and filled out while iterate through :meth:`TimeSeriesSearch.iterator`."""
    _df: Optional[GeoDataFrame] = None

    @property
    def ts(self) -> TimeSeries:
        """Retrieve the reference of Time Series context object."""
        if self._ts is None:
            _ = self.total_locations()

            if self._pagination is not None:
                for _ in self.iterator():
                    ...

        return self._ts

    def total_locations(self) -> int:
        """Retrieve total of locations matched using the given query conditions."""
        if self._ts is None:
            timeline = self.coverage.timeline
            if len(timeline) == 0:
                return 0

            ts = self._time_series(with_pagination=True)
            self._pagination = ts._pagination
            self._ts = ts
        return self._ts.total_locations

    def _pagination_allowed(self) -> bool:
        # TODO: Consider MultiPoint
        return self.query.pagination and self.query.geom.geom_type != 'Point'

    def _time_series(self, with_pagination) -> TimeSeries:
        query = asdict(self.query)
        if not self._pagination_allowed() or not with_pagination:
            query.pop('pagination', None)

        return self.coverage._timeseries(**query)

    def df(self, partial: bool = False) -> GeoDataFrame:
        """Create a GeoPandas dataframe with timeseries data.

        Args:
            partial (bool): use paginated values in cache from current page. Defaults to ``False``,
                which means generate DataFrame from all series.

        Raises:
            ImportError: If pandas or matplotlib could not be imported.
        """
        try:
            import matplotlib.pyplot as plt
            import pandas
        except:
            raise ImportError('Cannot import one of the following libraries: [pandas, matplotlib].')

        if self._df is None:
            if self._ts is None:
                total = self.total_locations()
            else:
                total = self._ts.total_locations

            attributes = []
            geoms = []
            series = []
            timeline = []

            fmt = "%Y-%m-%d"

            # Cache to avoid re-paginate time series
            if not partial and total > 0:
                location = list(self._ts._locations.values())[0]
                start_ref = datetime.fromisoformat(self.query.start_datetime.rstrip('Z')).strftime(fmt)
                end_ref = datetime.fromisoformat(self.query.end_datetime.rstrip('Z')).strftime(fmt)

                expected_timeline = [t for t in self.coverage.timeline if start_ref <= t <= end_ref]
                # When all timeline is present in a location, skip.
                # Otherwise, iterate over pagination to fill out.
                if location.timeline != expected_timeline:
                    for _ in self.iterator():
                        pass

            for attribute in self.query.attributes:
                for location in self._ts._locations.values():
                    series_ = location.series['values'][attribute]
                    attributes.extend([attribute] * len(series_))
                    series.extend(series_)
                    geoms.extend([location.geom] * len(series_))
                    timeline.extend(location.series['timeline'])

            self._df = GeoDataFrame({
                "attribute": attributes,
                "geometry": geoms,
                "value": series,
                "datetime": pandas.to_datetime(timeline, format=fmt),
            }, crs='EPSG:4326')

        return self._df

    def plot(self, paginate: bool = False, **kwargs):
        """Plot the time series on a chart.

        .. tip::

            If you are in Jupyter Notebooks and set ``paginate=True``, make sure
            to set ``%matplotlib notebook`` on top of notebook.

        Args:
            paginate (bool): Plot the data dynamically using pagination. Defaults to ``False``.

        Keyword Args:
            stats (bool): Flag to display time series statistics. Default is True.
                (Only applied on Time Series per Area)
            limit (int): Limit the number of time series to plot. Default is 1000.
                When None, display all. You may have performance issues.
            attributes (sequence): A sequence like ('red', 'nir') or ['red', 'nir']
        Raises:
            ImportError: If datetime, matplotlib or numpy or datetime could not be imported.
        """
        if not self._pagination_allowed():
            _ = self.total_locations()

            self._ts.plot(**kwargs)
            return

        if paginate:
            _ = self.total_locations()

            for ts in self.iterator():
                ts.plot(**kwargs)
            return
        ts = self._time_series(with_pagination=paginate)
        ts.plot(**kwargs)
        self._ts = ts

    def iterator(self, progress: bool = False) -> Iterator['TimeSeries']:
        """Iterate that yields :class:`wtss.timeseries.TimeSeries` instances for each time series group matching the given query parameters.

        Args:
            progress: Show progress bar while retrieving time series. Defaults to ``False``.

        Yields:
            TimeSeries: each TimeSeries matching the query criteria
        """
        import click

        ts_iterator = self._time_series_it()
        with click.progressbar(ts_iterator,
                               length=self._pagination['total_pages']) as bar:
            if self._ts is None:
                _ = self.total_locations()

            if progress:
                ts_iterator = bar

            yield self._ts

            for ts in ts_iterator:
                yield ts

    def _prepare_paginate(self, pagination: str):
        query = asdict(self.query)
        query['pagination'] = pagination
        ts = self.coverage._timeseries(**query)
        self._pagination = ts._data['pagination']

    def _next_time_series(self, page: int) -> TimeSeries:
        options = asdict(self.query)
        options.setdefault('params', {})
        options['params']['page'] = page
        return self.coverage._timeseries(**options)

    def _time_series_it(self):
        for page in range(self._pagination['next'], self._pagination['total_pages'] + 1):
            ts = self._next_time_series(page)

            # Modify global ctx
            self._modify_ts_context(ts)

            # yield self
            yield ts

    def _modify_ts_context(self, ts: TimeSeries):
        for idx, location in ts.locations.items():
            self_location = self._ts._locations[idx]

            self_location.extend(location)

        if ts._pagination.get('next'):
            self._pagination['next'] = ts._pagination['next']

    def summarize(self, operations: Optional[List[str]] = None,
                  masked: Optional[bool] = False,
                  mask: Any = None) -> Summarize:
        """Summarize Time Series object."""
        return self.coverage.summarize(operations=operations,
                                       masked=masked,
                                       mask=mask,
                                       geom=shapely.geometry.mapping(self.query.geom),
                                       start_datetime=self.query.start_datetime,
                                       end_datetime=self.query.end_datetime,
                                       attributes=self.query.attributes)
