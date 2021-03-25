#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2020-2021 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Command-Line Interface for BDC database management."""

import click

from .wtss import WTSS


@click.group()
@click.version_option()
def cli():
    """Database commands.

    .. note:: You can invoke more than one subcommand in one go.
    """


@cli.command()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-u', '--url', required=True, type=str,
              help='WTSS server address.')
@click.option('--access-token', required=False, type=str,
              help='User Personal Access Token.')
def list_coverages(verbose, url, access_token=None):
    """List available coverages."""
    if verbose:
        click.secho(f'Server: {url}', bold=True, fg='black')
        click.secho('\tRetrieving the list of available coverages... ',
                    bold=False, fg='black')

    service = WTSS(url, access_token=access_token)

    if verbose:
        for cv in service:
            click.secho(f'\t\t- {cv.name}', bold=True, fg='green')
    else:
        for cv in service.coverages:
            click.secho(f'{cv}', bold=True, fg='green')

    if verbose:
        click.secho('\tFinished!', bold=False, fg='black')


@cli.command()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-u', '--url', required=True, type=str,
              help='WTSS server address.')
@click.option('-c', '--coverage', required=True, type=str,
              help='Coverage name')
@click.option('--access-token', required=False, type=str,
              help='User Personal Access Token.')
def describe(verbose, url, coverage, access_token=None):
    """Retrieve the coverage metadata."""
    if verbose:
        click.secho(f'Server: {url}', bold=True, fg='black')
        click.secho('\tRetrieving the coverage metadata... ',
                    bold=False, fg='black')

    service = WTSS(url, access_token=access_token)

    cv = service[coverage]

    click.secho(f'\t- {cv}', bold=True, fg='green')

    if verbose:
        click.secho('\tFinished!', bold=False, fg='black')


@cli.command()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-u', '--url', required=True, type=str,
              help='WTSS server address.')
@click.option('-c', '--coverage', required=True, type=str,
              help='Coverage name')
@click.option('-a', '--attributes', required=False, type=str,
              help='Attribute list (items separated by comma)')
@click.option('--latitude', required=True, type=float,
              help='Latitude in EPSG:4326')
@click.option('--longitude', required=True, type=float,
              help='Longitude in EPSG:4326')
@click.option('--start-date', required=False, type=str,
              help='Start date')
@click.option('--end-date', required=False, type=str,
              help='End date')
@click.option('--access-token', required=False, type=str,
              help='User Personal Access Token.')
def ts(verbose, url, coverage, attributes,
       latitude, longitude, start_date, end_date, access_token=None):
    """Retrieve the coverage metadata."""
    if verbose:
        click.secho(f'Server: {url}', bold=True, fg='black')
        click.secho('\tRetrieving time series... ',
                    bold=False, fg='black')

    service = WTSS(url, access_token=access_token)

    cv = service[coverage]

    ts = cv.ts(latitude=latitude, longitude=longitude,
               attributes=attributes, start_date=start_date, end_date=end_date)

    for attr in ts.attributes:
        click.secho(f'\t{attr}: {ts.values(attr)}')

    click.secho(f'\ttimeline: {ts.timeline}')

    if verbose:
        click.secho('\tFinished!', bold=False, fg='black')
