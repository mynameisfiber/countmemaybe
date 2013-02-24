#!/usr/bin/env python2.7
"""
Install script for countmemaybe

micha gorelick, mynameisfiber@gmail.com
http://micha.gd/
"""

from setuptools import setup

setup(
    name = 'countmemaybe',
    version = '0.1',
    description = 'A set of probabilstic distinct value estimators (ie: '\
                  'calculate the cardinality of big sets)',
    author = 'Micha Gorelick',
    author_email = 'mynameisfiber@gmail.com',
    url = 'http://github.com/mynameisfiber/countmemaybe/',
    license = "GNU Lesser General Public License v3 or later (LGPLv3+)",

    classifiers = [
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    ],

    install_requires = [
        "mmh3",
        "blist",
    ],
    extras_require = {
        "kminvalue_relative_error" : ["scipy", ],
        "test_dve" : ["progressbar", ],
    }
)
