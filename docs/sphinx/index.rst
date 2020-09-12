..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2020 INPE.

    Python Client Library for WTSS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


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
    api
    repository
    history


.. toctree::
    :maxdepth: 1
    :caption: Additional Notes

    license


.. note::

    `WTSS Specification using OpenAPI 3.0 <https://github.com/brazil-data-cube/wtss-spec>`_.
