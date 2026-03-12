# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md', encoding = 'utf-8') as f:
    readme = f.read()

with open('LICENSE', encoding = 'utf-8') as f:
    license_text = f.read()

setup(
    name='pyseext',
    version='1.3.0',
    description='Python Selenium ExtJS - package for helping interact with an ExtJS application from Python using Selenium',
    long_description=readme,
    author='Martyn West',
    author_email='657393+westy@users.noreply.github.com',
    url='https://github.com/westy/pyseext',
    license=license_text,
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'pyseext': ['js/*.js']}
)
