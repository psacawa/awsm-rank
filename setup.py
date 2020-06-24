#!/usr/bin/env python3.7
from setuptools import setup, find_packages

setup(
    name="awsm-ranker",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["awsm-rank = awsm_ranker.awsm_rank:main"]
    },
)
