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

"""A class that represents a coverage in WTSS."""

import json
from typing import List, Union

import shapely.geometry
import shapely.wkb
from dateutil.parser import parse

from .summarize import Summarize
from .timeseries import TimeSeries
from .timeseries_search import TimeSeriesQuery, TimeSeriesSearch
from .utils import render_html

SUPPORTED_GEOMS = ('multipoint', 'point', 'polygon')


class Coverage(dict):
    """A class that describes a coverage in WTSS.

    .. note::

        For more information about coverage definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, service, metadata=None):
        """Create a coverage object associated to a WTSS client."""
        #: WTSS: The associated WTSS client to be used by the coverage object.
        self._service = service

        super(Coverage, self).__init__(metadata or {})

    @property
    def attributes(self):
        """Return the list of coverage attributes."""
        return [band for band in self['bands']]

    @property
    def crs(self):
        """Return the coordinate reference system metadata."""
        return self['bdc:crs']

    @property
    def description(self):
        """Return the coverage description."""
        return self['description']

    @property
    def dimensions(self):
        """Return the coverage dimensions metadata."""
        return self['raster_size']

    @property
    def name(self):
        """Return the coverage name."""
        return self['fullname']

    @property
    def spatial_extent(self):
        """Return the coverage spatial extent."""
        return shapely.geometry.shape(self['extent'])

    @property
    def timeline(self):
        """Return the coverage timeline."""
        return sorted(self['timeline'])

    @staticmethod
    def _check_input_parameters(**options):
        """Check the input parameters formats."""
        geom = options.get('geom')
        latitude = options.pop('latitude', None)
        longitude = options.pop('longitude', None)

        # Legacy properties.
        start_date = options.pop("start_date", None)
        end_date = options.pop("end_date", None)
        options.setdefault("start_datetime", start_date)
        options.setdefault("end_datetime", end_date)

        if geom is None and (latitude is None or longitude is None):
            raise RuntimeError('Missing parameter geom or latitude/longitude.')

        # Check if geometry exists and try to create geometry from lat and lon
        if geom is None:
            if latitude is None or longitude is None:
                raise ValueError("Argument geom or arguments latitude and longitude are mandatory.")

            if (type(latitude) not in (float, int)) or (type(longitude) not in (float, int)):
                raise ValueError("Arguments latitude and longitude must be numeric.")

            if latitude < -90.0 or latitude > 90.0:
                raise ValueError('latitude is out-of range [-90,90].')

            if longitude < -180.0 or longitude > 180.0:
                raise ValueError('longitude is out-of range [-180,180].')

            options['geom'] = dict(type="Point", coordinates=[longitude, latitude])

        # If geometry is a string, convert to GeoJSON
        elif isinstance(geom, str):
            try:
                options['geom'] = json.loads(geom)
            except json.JSONDecodeError:
                raise ValueError('Could not convert string geometry to GeoJSON.')

        # If geometry is a shapely object, convert to GeoJSON
        elif isinstance(geom, shapely.geometry.base.BaseGeometry):
            options['geom'] = shapely.geometry.mapping(geom)

        def _validate_datetime(key: str, fmt: str = "%Y-%m-%dT%H:%M:%SZ"):
            if options.get(key) is None:
                return
            try:
                dt = parse(options[key])
                options[key] = dt.strftime(fmt)
            except:
                raise ValueError(f'{key} could not be parsed.')

        if options['geom']['type'].lower() not in SUPPORTED_GEOMS:
            raise ValueError(f"Geometry {options['geom']} not supported. Use one of {SUPPORTED_GEOMS}")

        _validate_datetime('start_datetime')
        _validate_datetime('end_datetime')

        return options

    def ts(self, params=None, **options) -> TimeSeriesSearch:
        """Retrieve the time series."""
        # Check the parameters
        options_checked = self._check_input_parameters(**options)
        # Ensure to cast Geom to shapely
        options_checked['geom'] = shapely.geometry.shape(options_checked["geom"])

        query = TimeSeriesQuery(params=params or {}, **options_checked)

        return TimeSeriesSearch(coverage=self, query=query)

    def _timeseries(self, params=None, **options) -> TimeSeries:
        """Retrieve the time series."""
        # Check the parameters
        options_checked = self._check_input_parameters(**options)

        # Invoke timeseries request
        data = self._service._retrieve_timeseries_or_summarize(
            coverage_name=self.name,
            route='timeseries',
            params=params,
            **options_checked
        )
        return TimeSeries(self, data, **options_checked)

    def summarize(self, attributes: List[str],
                  geom: Union[str, shapely.geometry.base.BaseGeometry], **options):
        """Retrieve the Time Series summarize object.

        You may ask for a statistics method using the `operators` parameters.
        The following operators are supported: `mean`, `median`, `min`, `max`, `std`.
        By default, the WTSS server retrieves all aggregations when no operators given.

        Args:
            attributes (List[str]): A list of attributes to be applied in request.
            geom (dict|shapely.geometry.base.BaseGeometry): A GEOM object to filter.
        Keyword Args:
            start_datetime (str): The start datetime offset. Default None.
            end_datetime (str): The end datetime offset
            operations (List[str]): A list of specific operators to retrieve. Default None (All).
            masked (bool): Use cloud masking for summarization. Default is None.
            mask (Any): Optional cloud masking support. For BDC Cubes, the WTSS already deals with
                internal masking.
                See more in `Temporal Composition Masking <https://brazil-data-cube.github.io/products/specifications/processing-flow.html#temporal-compositing>`_.
        """
        # Check the parameters
        options_checked = self._check_input_parameters(attributes=attributes, geom=geom, **options)

        # Invoke timeseries request
        data = self._service._retrieve_timeseries_or_summarize(
            coverage_name=self.name,
            route='summarize',
            **options_checked
        )

        # Create Summarize object
        return Summarize(self, data)

    def __str__(self):
        """Return the string representation of the Coverage object."""
        return super().__str__()

    def __repr__(self):
        """Return the Coverage object representation."""
        wtss_repr = repr(self._service)

        text = f'Coverage(service={wtss_repr}, id={self.name})'

        return text

    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints WTSS."""
        return self._repr_html_()

    def _repr_html_(self):
        """Display the coverage metadata as HTML.

        This integrates a rich display in IPython.
        """
        html = render_html('coverage.html', coverage=self)

        return html
