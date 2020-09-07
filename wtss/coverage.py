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
        # attributes are displayed in nested table
        attr_rows = []

        for attr in self['attributes']:
            att_row_html = f'''
<tr>
    <td>{attr["name"]}</td>
    <td>{attr["description"]}</td>
    <td>{attr["datatype"]}</td>
    <td>{attr["valid_range"]}</td>
    <td>{attr["scale_factor"]}</td>
    <td>{attr["missing_value"]}</td>
</tr>'''
            attr_rows.append(att_row_html)

        # the spatial extent is show in nested table
        spatial_extent_row = f'''
<table border="1" class="coverage" style="width: 100%;">
    <thead>
        <tr>
            <th>xmin</th>
            <th>ymin</th>
            <th>xmax</th>
            <th>ymax</th>
        </tr>
    </thead>
    <tr>
        <td>{self["spatial_extent"]["xmin"]}</td>
        <td>{self["spatial_extent"]["ymin"]}</td>
        <td>{self["spatial_extent"]["xmax"]}</td>
        <td>{self["spatial_extent"]["ymax"]}</td>
    </tr>
</table>
'''

        # the timeline hides some values
        dates = []

        if len(self['timeline']) > 5:
            dates.extend(self['timeline'][0:4])
            dates.append(self['timeline'][-1])
        else:
            dates.extend(self['timeline'])

        timeline_row = ', '.join(dates[0:-1]) + ' ... ' + dates[-1]


        html =  '''\
<table border="1" class="coverage">
    <thead>
        <tr style="text-align: left;">
            <th colspan="2"><b>Coverage: {name}</b></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>Description</b></td>
            <td>{description}</td>
        </tr>
        <tr>
            <td><b>Attributes</b></td>
            <td>
                <table border="1" class="coverage" style="width: 100%;">
                    <thead>
                        <tr>
                            <th>name</th>
                            <th>description</th>
                            <th>datatype</th>
                            <th>valid range</th>
                            <th>scale</th>
                            <th>nodata</th>
                        </tr>
                    </thead>
                    {attributes}
                </table>
            </td>
        </tr>
        <tr>
            <td>Extent</td>
            <td>{spatial_extent}</td>
        </tr>
        <tr>
            <td>Timeline</td>
            <td>{timeline}</td>
        </tr>
    </tbody>
</table>'''.format(name=self['name'],
                   description=self['description'],
                   attributes=''.join(attr_rows),
                   spatial_extent=spatial_extent_row,
                   timeline=timeline_row)

        return html
