#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Command-Line Interface for BDC database management."""

import click


@click.group()
def cli():
    """Database commands.

    .. note:: You can invoke more than one subcommand in one go.
    """

@cli.command()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-u', '--url', required=True, type=str,
              help='WTSS server address.')
def list_coverages(verbose, url):
    """List available coverages.

    .. note:: You can invoke more than one subcommand in one go.
    """
    if verbose:
        click.secho('Retrieving the list of available coverages... ',
                    bold=False, fg='black', nl=False)

    if verbose:
        click.secho('OK!',
                    bold=True, fg='green')

        click.secho(f'\tServer: {url}',
                    bold=False, fg='black')
