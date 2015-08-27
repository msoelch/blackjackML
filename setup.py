#! /usr/bin/env python
# -*- coding: utf-8 -*-


# __author__ = ''


from setuptools import setup, find_packages


setup(
    name="blackjackML",
    version="pre-0.1",
    description="Black Jack simulation for Machine Learning purposes",
    license="FreeBSD",
    keywords="Black Jack, Machine Learning",
    packages=find_packages(exclude=['Notebooks']),
    include_package_data=True,
)

