#!/usr/bin/env python2.7
"""
Install script for countmemaybe

micha gorelick, mynameisfiber@gmail.com
http://micha.gd/
"""

from setuptools import setup

setup(
    name = 'countmemaybe',
    version = '0.3.3',
    description = 'A set of probabilstic distinct value estimators (ie: '\
                  'calculate the cardinality of big sets)',
    author = 'Micha Gorelick',
    author_email = 'mynameisfiber@gmail.com',
    url = 'http://github.com/mynameisfiber/countmemaybe/',
    download_url = 'https://github.com/mynameisfiber/countmemaybe/tarball/master',
    license = "GNU Lesser General Public License v3 or later (LGPLv3+)",

    classifiers = [
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    ],

    packages = ['countmemaybe',],

    install_requires = [
        "mmh3",
        "blist",
    ],
    extras_require = {
        "kminvalue_relative_error" : ["scipy", ],
        "test_dve" : ["progressbar", ],
    }
)
