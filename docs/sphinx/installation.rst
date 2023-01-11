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


.. _Installation:

Installation
============


Pre-Requirements
----------------


``wtss.py`` depends essentially on:

- `Requests <https://requests.readthedocs.io/en/master/>`_: an HTTP library for Python.

- `jsonschema <https://github.com/Julian/jsonschema>`_: an implementation of JSON Schema for Python. It is used to validate WTSS server responses.

- `Click <https://click.palletsprojects.com/en/7.x/>`_: a Python package for creating beautiful command line interfaces.


Please, read the instructions below in order to install ``wtss.py``.


Built Distributions
-------------------


Linux, macOS, and Windows users can get ``wtss`` from the `Python Package Index <https://pypi.org/project/wtss/>`_ with a recent version of ``pip``::

    pip install wtss


.. note::

    If you want to install the Matplotlib support, use the following command::

        pip install wtss[matplotlib]


Development Installation - GitHub
---------------------------------


Clone the Software Repository
+++++++++++++++++++++++++++++


Use ``git`` to clone the software repository::

    git clone https://github.com/brazil-data-cube/wtss.py.git


Install WTSS in Development Mode
++++++++++++++++++++++++++++++++


Go to the source code folder::

    cd wtss.py


Install in development mode::

    pip3 install -e .[all]


.. note::

    If you want to create a new *Python Virtual Environment*, please, follow this instruction:

    *1.* Create a new virtual environment linked to Python 3.7::

        python3.7 -m venv venv


    **2.** Activate the new environment::

        source venv/bin/activate


    **3.** Update pip and setuptools::

        pip3 install --upgrade pip

        pip3 install --upgrade setuptools


Run the Tests
+++++++++++++


.. code-block:: shell

     WTSS_TEST_URL="http://your-server" ./run-tests.sh


Build the Documentation
+++++++++++++++++++++++


You can generate the documentation based on Sphinx with the following command::

    python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under::

    docs/sphinx/_build/html/


You can open the above documentation in your favorite browser, as::

    firefox docs/sphinx/_build/html/index.html