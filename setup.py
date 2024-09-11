#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

"""Python Client Library for WTSS."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

history = open('CHANGES.rst').read()

docs_require = [
    'Sphinx>=2.2',
    'sphinx_rtd_theme',
    'sphinx-copybutton',
]

tests_require = [
    'coverage>=4.5',
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40',
]

examples_require = [
    'matplotlib>=3.1',
    'numpy>=1.18',
]

extras_require = {
    'docs': docs_require,
    'examples': examples_require,
    'tests': tests_require,
    'matplotlib': ['numpy>=1.13', 'matplotlib>=3.1,<4']
}

extras_require['all'] = [req for _, reqs in extras_require.items() for req in reqs]

setup_requires = [
    'pytest-runner>=5.2',
]

install_requires = [
    'Click>=7.0',
    'geopandas>=0.12',
    'jsonschema>=3.2',
    'requests>=2.20',
    'Jinja2>=2.10',
    'python-dateutil>=2.8',
    'Shapely>=1.8'
]

packages = find_packages()

g = {}
with open(os.path.join('wtss', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='wtss',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    keywords=['Web Time Series Service', 'Time series', 'Earth Observations'],
    license='GPLv3',
    author='Brazil Data Cube Team',
    author_email='brazildatacube@inpe.br',
    url='https://github.com/brazil-data-cube/wtss.py',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'wtss = wtss.cli:cli',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
