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

from .timeseries import TimeSeries
from .utils import render_html


class Coverage(dict):
    """A class that describes a coverage in WTSS.

    .. note::

        For more information about coverage definition, please, refer to
        `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.
    """

    def __init__(self, service, metadata=None):
        """Create a coverage object associated to a WTSS client.

        Args:
            service (wtss.wtss.WTSS): The client to be used by the coverage object.
            metadata (dict): The coverage metadata.
        """
        #: WTSS: The associated WTSS client to be used by the coverage object.
        self._service = service

        super(Coverage, self).__init__(metadata or {})


    @property
    def attributes(self):
        """Return the list of coverage attributes."""
        return self['attributes']


    @property
    def crs(self):
        """Return the coordinate reference system metadata."""
        return self['crs']


    @property
    def description(self):
        """Return the coverage description."""
        return self['description']


    @property
    def dimensions(self):
        """Return the coverage dimensions metadata."""
        return self['dimensions']


    @property
    def name(self):
        """Return the coverage name."""
        return self['name']


    @property
    def spatial_extent(self):
        """Return the coverage spatial extent."""
        return self['spatial_extent']


    @property
    def spatial_resolution(self):
        """Return the coverage spatial resolution metadata."""
        return self['spatial_resolution']


    @property
    def timeline(self):
        """Return the coverage timeline."""
        return self['timeline']


    def ts(self, **options):
        """Retrieve the time series for a given location and time interval.

        Keyword Args:
            attributes (optional): A string with attribute names separated by commas,
                or any sequence of strings. If omitted, the values for all
                coverage attributes are retrieved.
            longitude (int/float): A longitude value according to EPSG:4326.
            latitude (int/float): A latitude value according to EPSG:4326.
            start_date (:obj:`str`, optional): The begin of a time interval.
            end_date (:obj:`str`, optional): The begin of a time interval.

        Returns:
            TimeSeries: A time series object as a dictionary.

        Raises:
            HTTPError: If the server response indicates an error.
            ValueError: If the response body is not a json document.
            ImportError: If Maptplotlib or Numpy can no be imported.

        Example:

            Retrieves a time series for MODIS13Q1 data product:

            .. doctest::
                :skipif: WTSS_EXAMPLE_URL is None

                >>> from wtss import *
                >>> service = WTSS(WTSS_EXAMPLE_URL)
                >>> coverage = service['MOD13Q1']
                >>> ts = coverage.ts(attributes=('red', 'nir'),
                ...                  latitude=-12.0, longitude=-54.0,
                ...                  start_date='2001-01-01', end_date='2001-12-31')
                ...
                >>> ts.red
                [236.0, 289.0, ..., 494.0, 1349.0]
        """
        attributes = options['attributes'] \
                        if 'attributes' in options and options['attributes'] \
                            else [attr['name'] for attr in self.attributes]

        if not isinstance(attributes, str):
            attributes = ','.join(attributes)

        if ('latitude' not in options) or ('longitude' not in options):
            raise ValueError("Arguments latitude and longitude are mandatory.")

        latitude = options['latitude']
        longitude = options['longitude']

        if (type(latitude) not in (float, int)) or (type(longitude) not in (float, int)):
            raise ValueError("Arguments latitude and longitude must be numeric.")

        if (latitude < -90.0) or (latitude > 90.0):
            raise ValueError('latitude is out-of range [-90,90]!')

        if (longitude < -180.0) or (longitude > 180.0):
            raise ValueError('longitude is out-of range [-180,180]!')

        start_date = options['start_date'] if ('start_date' in options) else self.timeline[0]

        end_date = options['end_date'] if ('end_date' in options) else self.timeline[-1]

        data = self._service._time_series(coverage=self.name, attributes=attributes,
                                          longitude=longitude, latitude=latitude,
                                          start_date=start_date, end_date=end_date)

        return TimeSeries(self, data)


    def __str__(self):
        """Return the string representation of the Coverage object."""
        return super().__str__()


    def __repr__(self):
        """Return the Coverage object representation."""
        wtss_repr = repr(self._service)

        text = f'Coverage(service={wtss_repr}, metadata={super().__repr__()}'

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