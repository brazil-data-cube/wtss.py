..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2020-2021 INPE.

    Python Client Library for WTSS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


=================================================
Python Client Library for Web Time Series Service
=================================================


.. image:: https://img.shields.io/badge/license-MIT-green
        :target: https://github.com//brazil-data-cube/wtss.py/blob/master/LICENSE
        :alt: Software License


.. image:: https://drone.dpi.inpe.br/api/badges/brazil-data-cube/wtss.py/status.svg
        :target: https://drone.dpi.inpe.br/brazil-data-cube/wtss.py
        :alt: Build Status


.. image:: https://codecov.io/gh/brazil-data-cube/wtss.py/branch/master/graph/badge.svg?token=E7F8BA09JF
        :target: https://codecov.io/gh/brazil-data-cube/wtss.py
        :alt: Code Coverage Test


.. image:: https://readthedocs.org/projects/wtss/badge/?version=latest
        :target: https://wtss.readthedocs.io/en/latest/
        :alt: Documentation Status


.. image:: https://img.shields.io/badge/lifecycle-maturing-blue.svg
        :target: https://www.tidyverse.org/lifecycle/#maturing
        :alt: Software Life Cycle


.. image:: https://img.shields.io/github/tag/brazil-data-cube/wtss.py.svg
        :target: https://github.com/brazil-data-cube/wtss.py/releases
        :alt: Release


.. image:: https://img.shields.io/pypi/v/wtss
        :target: https://pypi.org/project/wtss/
        :alt: Python Package Index


.. image:: https://img.shields.io/discord/689541907621085198?logo=discord&logoColor=ffffff&color=7389D8
        :target: https://discord.com/channels/689541907621085198#
        :alt: Join us at Discord


About
=====


**W**\ eb **T**\ ime **S**\ eries **S**\ ervice (WTSS) is a lightweight web service for handling time series data from remote sensing imagery. Given a location and a time interval you can retrieve the according time series as a list of real values.


In WTSS a coverage is a three dimensional array associate to spatial and temporal reference systems.


.. image:: https://raw.githubusercontent.com/brazil-data-cube/wtss.py/master/docs/sphinx/img/image-time-series.png
    :target: https://github.com/brazil-data-cube/wtss.py/blob/master/docs/sphinx/img/image-time-series.png
    :width: 240
    :alt: Coverage as a three dimensional array


WTSS is based on three operations:

- ``list_coverages``: returns the list of all available coverages in the service.

- ``describe_coverage``: returns the metadata of a given coverage.

- ``time_series``: query the database for the list of values for a given location and time interval.


If you want to know more about WTSS service, please, take a look at its `specification <https://github.com/brazil-data-cube/wtss-spec>`_.


Installation
============


Linux, macOS, and Windows users can get ``wtss`` from the `Python Package Index <https://pypi.org/project/wtss/>`_ with a recent version of ``pip``::

    pip install wtss


.. note::

    If you want to install the Matplotlib support, use the following command::

        pip install wtss[matplotlib]


Documentation
=============


See https://wtss.readthedocs.io/en/latest/.


References
==========


VINHAS, L.; QUEIROZ, G. R.; FERREIRA, K. R.; CÂMARA, G. `Web Services for Big Earth Observation Data <http://www.seer.ufu.br/index.php/revistabrasileiracartografia/article/view/44004>`_. Revista Brasileira de Cartografia, v. 69, n. 5, 18 maio 2017.


License
=======


.. admonition::
    Copyright (C) 2020-2021 INPE.

    Python Client Library for WTSS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.
