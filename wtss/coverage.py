#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a coverage in WTSS."""

from .timeseries import TimeSeries
from .summarize import Summarize
from .utils import render_html
import shapely.geometry
import json
from dateutil.parser import parse


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
        return [band['name'] for band in self['properties']['eo:bands']]


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


    @staticmethod
    def _check_input_parameters(self, options):

        # -------------------------------------------------------------------------
        # Check geometry

        geom = options['geom'] if 'geom' in options.keys() else None
        latitude = options['latitude'] if 'latitude' in options.keys() else None
        longitude = options['longitude'] if 'longitude' in options.keys() else None
        
        # Remove lat and/or lon if geom exists
        if geom is not None and latitude is not None:
            options.pop('latitude') 
        if geom is not None and longitude is not None:
            options.pop('longitude') 

        # Check if geometry exists and try to create geometry from lat and lon
        if geom is None:
            if latitude==None or longitude==None:
                raise ValueError("Argument geom or arguments latitude and longitude are mandatory.")
            
            if (type(latitude) not in (float, int)) or (type(longitude) not in (float, int)):
                raise ValueError("Arguments latitude and longitude must be numeric.")

            if latitude<-90.0 or latitude>90.0:
                raise ValueError('latitude is out-of range [-90,90].')

            if longitude<-180.0 or longitude>180.0:
                raise ValueError('longitude is out-of range [-180,180].')

            options['geom'] = dict(type="Point", coordinates=[longitude, latitude])

        # If geometry is a string, convert to GeoJSON
        elif isinstance(geom, str):
            try:
                options['geom'] = json.loads(geom)
            except:
                raise ValueError('Could not convert string geometry to GeoJSON.')

        # If geometry is a shapely object, convert to GeoJSON
        elif isinstance(geom, shapely.geometry.base.BaseGeometry):
            options['geom'] = shapely.geometry.mapping(geom)
        
        # -------------------------------------------------------------------------
        # Check start_datetime

        if 'start_datetime' in options.keys():
            try:
                dt = parse(options['start_datetime'])
                options['start_datetime'] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except:
                raise ValueError('start_datetime could not be parsed.')


        # -------------------------------------------------------------------------
        # Check end_datetime

        if 'end_datetime' in options.keys():
            try:
                dt = parse(options['end_datetime'])
                options['end_datetime'] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except:
                raise ValueError('end_datetime could not be parsed.')

        # -------------------------------------------------------------------------
        # Return options object checked
        return options


    def ts(self, **options):
        """Retrieve the time series for a given location and time interval."""

        # Check the parameters
        options_checked = self._check_input_parameters(self, options)
        
        # Invoke timeseries request
        data = self._service._retrieve_timeseries_or_summarize( coverage_name = self.name, 
                                                                route = 'timeseries', 
                                                                options = options_checked)

        # Create timeseries object
        return TimeSeries(self, data)


    def summarize(self, **options):
        """Retrieve the summarized time series for a given location and time interval."""
        
        # Check the parameters
        options_checked = self._check_input_parameters(self, options)

        # Invoke timeseries request
        data = self._service._retrieve_timeseries_or_summarize( coverage_name = self.name, 
                                                                route = 'summarize', 
                                                                options = options_checked)

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
