# -*- coding: utf-8 -*-

import os

from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='APSchedulerSocket',
    version='0.4.1',
    description="The purpose of the application is to solve the problem of having a unique 'APScheduler' object for a multithreaded application. The project aims to easily implement a client-server architecture to control the scheduled processes. Another great advantage is that you can use the scheduler in distributed processes or servers.",
    long_description=read('README.rst') +
                     read('HISTORY.rst') +
                     read('LICENSE'),
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Rodrigo Ristow',
    author_email='rodrigo@maxttor.com',
    url='',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'APScheduler',
    ],
    extras_require={
        'test': [
            'nose',
            'nose-selecttests',
            'coverage',
            'unittest2',
            'flake8',
        ],
        'development': [
            'zest.releaser',
            'check-manifest',
        ],
    },
    entry_points="""
    """,
    include_package_data=True,
    zip_safe=False,
)
