#!/usr/bin/env python


from setuptools import setup, find_packages


setup(
    name='simpleconfig',
    version='0.1.0',
    description='Simple configuration for Python projects.',
    author='David McClure',
    author_email='dclure@mit.edu',
    url='https://github.com/davidmcclure/simpleconfig',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'anyconfig',
        'voluptuous',
        'PyYAML',
    ],
)
