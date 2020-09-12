..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2020 INPE.

    Python Client Library for WTSS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Usage
=====


Creating a Python code to retrieve a time series
------------------------------------------------


Import the ``wtss`` class and then use it to create an object to retrieve the time series as shown in the following example:


.. code-block:: python

    from wtss import *

    service = WTSS('http://www.esensing.dpi.inpe.br')


The object ``service`` allows to list the available coverages:


.. code-block:: python

    print(service.coverages)


Result::

    ['MOD13Q1', 'MOD13Q1_M']


It also allows to retrieve a coverage object with its metadata:


.. code-block:: python

    coverage = service['MOD13Q1']

    print(coverage)


Result::

    Coverage: MOD13Q1


In order to retrieve the time series for attributes ``red`` and ``nir``, in the location of ``latitude -12`` and ``longitude -54`` from ``January 1st, 2001`` tp ``December 31st, 2001``, use the ``ts`` method:


.. code-block:: python

    ts = coverage.ts(attributes=('red', 'nir'),
                     latitude=-12.0, longitude=-54.0,
                     start_date='2001-01-01', end_date='2001-12-31')


Then, you can access the time series values through the name of the attributes:


.. code-block:: python

    print('red values:', ts.red)

    print('nir values:', ts.nir)


Result::

    red values: [236.0, 289.0, ..., 494.0, 1349.0]

    nir values: [3463.0, 3656.0, ..., 3901.0, 2948.0]


It is also possible to access the time points associated to the values:


.. code-block:: python

    print(ts.timeline)


Result::

    [datetime.date(2001, 1, 1), ..., datetime.date(2001, 12, 19)]


If you have Matplotlib and Numpy, it is possible to plot the time series with the ``plot`` method:


.. code-block:: python

    ts.plot()


.. image:: ./img/ts_plot.png
        :alt: Time Series
        :width: 640px


More examples can be found in the :ref:`Section Examples <Examples>`.


Command-Line Interface (CLI)
----------------------------


The ``WTSS`` client installs a command line tool named ``wtss`` that allows to retrive time series data.


If you want to know the WTSS version, use the option ``--version`` as in::

    wtss --version


Output::

    wtss, version 0.7.0.post0


To list the available coverages in a service, use the ``list-coverages`` command and provides a URL to the ``--url`` option::

    wtss list-coverages --url http://localhost


Output::

    MOD13Q1
    MOD13Q1_M


To get more information about a specific coverage, use the ``describe`` command::

    wtss describe --coverage MOD13Q1 --url localhost


Output:


.. code-block:: json

    {
        "name": "MOD13Q1",
        "description": "Vegetation Indices 16-Day L3 Global 250m",
        "detail": "https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table/mod13q1_v006",
        "dimensions": { },
        "spatial_extent": { },
        "spatial_resolution": { },
        "crs": { },
        "timeline": [ ],
        "attributes": [ ]
    }


Finally, to retrieve the time series over a coverage in a specific location::

    wtss ts --coverage MOD13Q1 \
            --attributes red \
            --longitude -54 --latitude -12 \
            --start-date 2001-01-01 --end-date 2001-12-31 \
            --url http://localhost


If you want to know more about commands and their options, use the help::

    wtss --help

    wtss describe --help