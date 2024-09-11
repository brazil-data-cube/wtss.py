..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2024 INPE.

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


Changes
=======

Version 2.0.0.alpha3 (2024-09-11)
---------------------------------

- Fix time series plot related Axes object iteration (close #98)
- Fix unmapped properties `start_date` and `pixel_size` (close #105)


Version 2.0.0.alpha1 (2024-08-27)
---------------------------------

- Add support to deal with WTSS Server 2.0 (`#72 <https://github.com/brazil-data-cube/wtss.py/issues/72>`_)
- Add pagination and progress bar to retrieve time series by area (`#86 <https://github.com/brazil-data-cube/wtss.py/issues/86>`_)
- Plot time series quantile (`#84 <https://github.com/brazil-data-cube/wtss.py/issues/84>`_)
- Add way to retrieve and plot time series summarization (avg, standard_deviation, mean, etc) (`#78 <https://github.com/brazil-data-cube/wtss.py/issues/78>`_)
- Builtin way to transform time series object into GeoPandas (`#75 <https://github.com/brazil-data-cube/wtss.py/issues/75>`_)
- Scale time series (`#61 <https://github.com/brazil-data-cube/wtss.py/issues/61>`_)


Version 0.7.0 (2022-09-28)
--------------------------

- Change LICENSE to GPL v3
- Review docs and links


Version 0.7.0-3 (2021-03-29)
----------------------------


- Add the property ``common_name`` to the ``describe_coverage`` HTML representation: `#63 <https://github.com/brazil-data-cube/wtss.py/issues/63>`_.



Version 0.7.0-2 (2021-03-17)
----------------------------


- Addedd ``access token`` to the client API: `#57 <https://github.com/brazil-data-cube/wtss.py/issues/57>`_.

- Using Jinja 2 templates for Jupyter HTML output: `#51 <https://github.com/brazil-data-cube/wtss.py/issues/51>`_.

- Using Drone: `#54 <https://github.com/brazil-data-cube/wtss.py/issues/54>`_.


Version 0.7.0-1 (2020-09-14)
----------------------------


- Improved integration with Jupyter Environment: `#25 <https://github.com/brazil-data-cube/wtss.py/issues/25>`_.

- Improved ``plot`` method for ``TimeSeries``.

- Added Unit-tests.

- Fixed small typos in documentation.


Version 0.7.0-0 (2020-09-11)
----------------------------


- Basic integration with Jupyter Environment and Matplotlib.

- Command Line Interface (CLI).

- Documentation system based on Sphinx.

- Documentation integrated to ``Read the Docs``.

- Installation and build instructions.

- Package support through Setuptools.

- Installation and usage instructions.

- Travis CI support and PyPI deploy.

- Unit-test environment set.

- Source code versioning based on `Semantic Versioning 2.0.0 <https://semver.org/>`_.

- License: `MIT <https://github.com/gqueiroz/wtss.py/blob/master/LICENSE>`_.
