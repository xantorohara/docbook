#!/usr/bin/env python

from distutils.core import setup

setup(
    name='DocBook',
    version='1.2',
    description='Generate html book or static site from Markdown files',
    author='Xantorohara',
    author_email='xantorohara@gmail.com',
    url='https://github.com/xantorohara/docbook',
    packages=['docbook'], requires=['markdown']
)
