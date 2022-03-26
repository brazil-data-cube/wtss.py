#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a coverage in WTSS."""

from timeseries import TimeSeries
from utils import render_html


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
        return self['cube:dimensions']['bands']['values']


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
        return self['cube:dimensions']


    @property
    def name(self):
        """Return the coverage name."""
        return self['id']


    @property
    def spatial_extent(self):
        """Return the coverage spatial extent."""
        return self['extent']['spatial']['bbox'][0]


    # @property
    # def spatial_resolution(self):
    #     """Return the coverage spatial resolution metadata."""
    #     return self['extent']


    @property
    def timeline(self):
        """Return the coverage timeline."""
        return self['cube:dimensions']['temporal']['values']



    def convert_geom_to_shapely(geom):
        """Convert the geometry parameter to shapely object."""
        
        import json
        import shapely
        
        try:
            if isinstance(query_geom, str):
                query_geom = json.loads(query_geom)

            # Convert query geometry to shapely object
            geom = shapely.geometry.shape(query_geom)
            return geom
        except:
            return None


    def ts(self, 
            attributes=None, 
            geom=None, 
            latitude=None, 
            longitude=None, 
            start_datetime=None, 
            end_datetime=None, 
            applyAttributeScale=False, 
            pixelCollisionType='center'):
            
        """Retrieve the time series for a given location and time interval.

        Keyword Args:
            attributes (optional): A string with attribute names separated by commas,
                or any sequence of strings. If omitted, the values for all
                coverage attributes are retrieved.
            longitude (int/float): A longitude value according to EPSG:4326.
            latitude (int/float): A latitude value according to EPSG:4326.
            start_datetime (:obj:`str`, optional): The begin of a time interval.
            end_datetime (:obj:`str`, optional): The begin of a time interval.

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
                ...                  start_datetime='2001-01-01', end_datetime='2001-12-31')
                ...
                >>> ts.red
                [236.0, 289.0, ..., 494.0, 1349.0]
        """

        # Check attributes
        if attributes is not None:
            [attr for attr in self.attributes]

        # Check geometry
        if geom is None:
            if latitude==None or longitude==None:
                raise ValueError("Argument geom or arguments latitude and longitude are mandatory.")

            if (type(latitude) not in (float, int)) or (type(longitude) not in (float, int)):
                raise ValueError("Arguments latitude and longitude must be numeric.")

            if latitude<-90.0 or latitude>90.0:
                raise ValueError('latitude is out-of range [-90,90].')

            if longitude<-180.0 or longitude>180.0:
                raise ValueError('longitude is out-of range [-180,180].')

            geom = dict(type="Point", coordinates=[longitude, latitude])

        data = self._service._time_series(coverage = self.name, 
                                          attributes = attributes,
                                          geom = geom,
                                          start_datetime = start_datetime, 
                                          end_datetime = end_datetime,
                                          applyAttributeScale = applyAttributeScale,
                                          pixelCollisionType = pixelCollisionType)

        return TimeSeries(self, data)

    def summarize(self, **options):
        """TODO: Implement"""

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
