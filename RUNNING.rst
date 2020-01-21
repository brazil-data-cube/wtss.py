..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2019 INPE.

    Python Client Library for WTSS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Using wtss.py to retrieve the time series
=========================================

Import the ``wtss`` class and then use it to create an object to retrieve the time series as shown in the following example:

.. code-block:: python

        from wtss import wtss

        w = wtss("http://www.myserver.org")


        cv_list = w.list_coverages()

        print(cv_list)


        cv_scheme = w.describe_coverage("mod13q1_512")

        print(cv_scheme)


        ts = w.time_series("mod13q1_512", ("red", "nir"), -12.0, -54.0, "", "")

        print(ts["red"])

        print(ts["nir"])

        print(ts.timeline)


If you want to plot a time series, you can write a code like:

.. code-block:: python

        import matplotlib.pyplot as pyplot
        import matplotlib.dates as mdates
        from wtss import wtss

        w = wtss("http://www.myserver.org")

        # retrieve the time series for location with longitude = -54, latitude =  -12
        ts = w.time_series("mod13q1_512", "red", -12.0, -54.0, start_date="2001-01-01", end_date="2001-12-31")

        fig, ax = pyplot.subplots()

        ax.plot(ts.timeline, ts["red"], 'o-')

        fig.autofmt_xdate()

        pyplot.show()


The codesnippet above will result in a chart such as:


.. image:: ./doc/img/ts_plot.png
        :alt: Time Series
        :width: 600px


More examples can be found in the examples directory.

