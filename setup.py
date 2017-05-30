#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='gitstats',
    version='1.0',
    description='Git Statistic Utility',
    author='Matt Chalmers (originally Heikki Hokkanen)',
    packages = find_packages(exclude=['build','dist']),
    package_data = {
            # Include *.gif or *.js files in the 'reporter' package:
            'gitstats.reporter': ['*.gif', '*.js', '*.css'],
        },
    entry_points={
        'console_scripts': [
            'gitstats = gitstats:main',
        ],
    }
)
