#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="awsm-ranker",
    version=open('VERSION').read().strip('\n'),
    description="Ranks github repo entries on github pages from the 'Awesome' series",
    author="Paweł Sacawa",
    url='https://github.com/psacawa/awsm-ranker',
    packages=find_packages(),
    entry_points={
        "console_scripts": ["awsm-rank = awsm_ranker.awsm_rank:main"]
    },
)
