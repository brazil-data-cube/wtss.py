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


The ``WTSS`` client installs a command line tool named ``wtss`` that allows to retrive time series data:

- **UNDER DEVELOPMENT**


.. .. automodule:: wtss.cli