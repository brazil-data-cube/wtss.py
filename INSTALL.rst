..
    This file is part of Python Client Library for WTSS.
    Copyright (C) 2019 INPE.

    Python Client Library for WTSS is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Installation
============

``wtss.py`` depends essentially on `Requests <https://requests.readthedocs.io/en/master/>`_. Please, read the instructions below in order to install ``wtss.py``.


Production installation
-----------------------

**Under Development!**

.. Install from `PyPI <https://pypi.org/>`_:
..
.. .. code-block:: shell
..
..     $ pip3 install wtss


Development installation
------------------------

Clone the software repository:

.. code-block:: shell

        $ git clone https://github.com/brazil-data-cube/wtss.py.git


Go to the source code folder:

.. code-block:: shell

        $ cd wtss.py


Install in development mode:

.. code-block:: shell

        $ pip3 install -e .[all]


Run the tests:

.. code-block:: shell

        $ ./run-test.sh


Generate the documentation:

.. code-block:: shell

        $ python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under:

.. code-block:: shell

    doc/sphinx/_build/html/
