..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2022 INPE.

    Python Client Library for WTSS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


.. _Examples:

Examples
========


List Available Coverages
-------------------------------


This example shows the available coverages in WTSS.


.. literalinclude:: ../../examples/list_coverages.py
   :language: python
   :lines: 11-


Summarize Time Series
-------------------------------


This example shows how to retrieve a summarized time series.


.. literalinclude:: ../../examples/sm.py
   :language: python
   :lines: 11-


Date Formats
-------------------------------


This example shows how different formats can be used to datetime.


.. literalinclude:: ../../examples/ts_and_sm_date_format.py
   :language: python
   :lines: 11-


Lat Long Example
-------------------------------


This example shows how to query data with lat long.


.. literalinclude:: ../../examples/ts_and_sm_geom_latlong.py
   :language: python
   :lines: 11-


Shapely Object Geometry
-------------------------------


This example shows how to use a shapely geometry for the request.


.. literalinclude:: ../../examples/ts_and_sm_geom_shapely.py
   :language: python
   :lines: 11-


Jupyter Notebook Example
-------------------------------


This is a WTSS Client in a jupyter notebook.


.. literalinclude:: ../../examples/WTSS_jupyter_notebook.ipynb
   :language: python
   :lines: 11-