#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="awsm-rank",
    version=open('VERSION').read().strip('\n'),
    description="Ranks github repo entries on github pages from the 'Awesome' series",
    author="Paweł Sacawa",
    url='https://github.com/psacawa/awsm-rank',
    packages=find_packages(),
    entry_points={
        "console_scripts": ["awsm-rank = awsm_rank.awsm_rank:main"]
    },
    install_requires = [
        "aiohttp",
        "bs4",
        "tabulate",
        "requests",
        "shtab",
    ]
)
