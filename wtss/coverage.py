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

    def __init__(self, service, metadata=None):
        """Create a coverage object associated to a WTSS client.

        Args:
            service (wtss): The client to be used by the coverage object.
            metadata (dict): The coverage metadata.
        """
        self._service = service
        super(Coverage, self).__init__(metadata or {})


    def __str__(self):
        """Return the string representation of the Coverage object."""
        text = f'Coverage: {self["name"]}'

        return text


    def __repr__(self):
        """Return the Coverage object representation."""
        wtss_repr = repr(self._service)

        text = f'Coverage(service={wtss_repr}, metadata={super().__repr__()}'

        return text


    def _repr_pretty_(self, p, cycle):
        """Customize how the REPL pretty-prints WTSS."""
        return self._repr_html_()


    def _repr_html_(self):
        """Display the coverage metadata as HTML.

        This integrates a rich display in IPython.
        """
        attr_rows = []

        for attr in self['attributes']:
            att_row_html = f'''\
<tr>
    <td>{attr["name"]}</td>
    <td>{attr["description"]}</td>
    <td>{attr["datatype"]}</td>
    <td>{attr["valid_range"]}</td>
    <td>{attr["scale_factor"]}</td>
    <td>{attr["missing_value"]}</td>
</tr>'''

            attr_rows.append(att_row_html)

        # shows timeline in a list
        timeline_htlm = '''\
<select id="timeline" size="10">
'''

        timeline_options = [f'<option value="{d}">{d}</option>' for d in self['timeline']]

        timeline_htlm += ''.join(timeline_options) + '</select>'

        html = '''\
<table>
    <thead>
        <tr>
           <th>Coverage</th>
           <td colspan="6">{name}</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th>Description</th>
            <td colspan="6">{description}</td>
        </tr>
        <tr>
            <th rowspan="{nattrs}">Attributes</th>
            <th>name</th>
            <th>description</th>
            <th>datatype</th>
            <th>valid range</th>
            <th>scale</th>
            <th>nodata</th>
        </tr>
        {attributes}
        <tr>
            <th rowspan="2">Extent</th>
            <th>xmin</th>
            <th>ymin</th>
            <th>xmax</th>
            <th colspan="3">ymax</th>
        </tr>
        <tr>
            <td>{xmin}</td>
            <td>{ymin}</td>
            <td>{xmax}</td>
            <td colspan="3">{ymax}</td>
        </tr>
        <tr>
            <th>Timeline</th>
            <td>{timeline}</td>
        </tr>
    </tbody>
</table>'''.format(name=self['name'],
                   description=self['description'],
                   attributes=''.join(attr_rows),
                   nattrs=len(attr_rows) + 1,
                   timeline=timeline_htlm,
                   **self['spatial_extent'])

        return html