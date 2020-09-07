#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""A class that represents a coverage in WTSS."""


class Coverage(dict):
    """A class that describes a coverage in WTSS.

    For more information about coverage definition, please, refer to
    `WTSS specification <https://github.com/brazil-data-cube/wtss-spec>`_.

    Attributes:

        _service (wtss): The associated WTSS client to be
            used by the coverage object.
    """

    def __init__(self, service, metadata):
        """Create a coverage object associated to a WTSS client.

        Args:
            service (wtss): The client to be used by the coverage object.
        """
        self._service = service

        super(Coverage, self).__init__(metadata or {})

    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints WTSS."""
        return self._repr_html_()


    def _repr_html_(self):
        """Display the coverage metadata as HTML.

        This integrates a rich display in IPython.
        """
        html =  '''\
<table border="1" class="coverage">
    <thead>
        <tr style="text-align: right;">
            <th colspan="2"><b>Coverage:</b></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>description</td>
            <td>...</td>
        </tr>
        <tr>
            <td>attributes</td>
            <td>...</td>
        </tr>
        <tr>
            <td>spatial_extent</td>
            <td>...</td>
        </tr>
        <tr>
            <td>timeline</td>
            <td>...</td>
        </tr>
    </tbody>
</table>'''

        return html
