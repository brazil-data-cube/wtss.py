..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2022 INPE.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


.. include:: ../../README.rst
   :end-before: About


**W**\ eb **T**\ ime **S**\ eries **S**\ ervice (WTSS) is a lightweight web service for handling time series data from remote sensing imagery. Given a location and a time interval you can retrieve the according time series as a Python list of real values.


In WTSS a coverage is a three dimensional array associate to spatial and temporal reference systems (:numref:`Figure %s <wtss:coverage>`).


.. figure:: ./img/image-time-series.png
    :alt: Coverage as a three dimensional array
    :width: 240
    :figclass: align-center
    :name: wtss:coverage

    A coverage as a three dimensional array.


WTSS is based on three operations:

- ``list_coverages``: returns the list of all available coverages in the service.

- ``describe_coverage``: returns the metadata of a given coverage.

- ``time_series``: query the database for the list of values for a given location and time interval.


.. toctree::
    :hidden:

    self


.. toctree::
    :maxdepth: 2
    :caption: Documentation:

    installation
    usage
    examples
    jupyter
    api
    repository
    history


.. toctree::
    :maxdepth: 1
    :caption: Additional Notes

    license


.. note::

    `WTSS Specification using OpenAPI 3.0 <https://github.com/brazil-data-cube/wtss-spec>`_.
