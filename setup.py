# -*- coding: utf-8 -*-
import os.path
import re
import sys
from setuptools import setup


py_version = sys.version_info[:2]
PY3 = py_version[0] == 3
PY26 = py_version == (2, 6)
if PY3:
    if py_version < (3, 2):
        raise RuntimeError(
            'On Python 3, Blogofile requires Python 3.2 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError(
            'On Python 2, Blogofile requires Python 2.6 or better')

with open('README.rst', 'rt') as readme:
    long_description = readme.read()
with open('CHANGES.txt', 'rt') as changes:
    long_description += '\n\n' + changes.read()

dependencies = [
    'Blogofile',
    'six',
    ]
if PY26:
    dependencies.append('argparse')


def find_package_data(module, path):
    """Find all data files to include in the package.
    """
    files = []
    exclude = re.compile("\.pyc$|~$")
    for dirpath, dirnames, filenames in os.walk(os.path.join(module, path)):
        for filename in filenames:
            if not exclude.search(filename):
                files.append(
                    os.path.relpath(os.path.join(dirpath, filename), module))
    return {module: files}

classifiers = [
    'Programming Language :: Python :: {0}'.format(py_version)
    for py_version in ['2', '2.6', '2.7', '3', '3.2']]
classifiers.extend([
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: Implementation :: CPython',
    'Environment :: Console',
    'Natural Language :: English',
])

setup(
    name="blogofile_blog",
    version="0.8b1",
    description="A simple blog engine plugin for Blogofile",
    long_description=long_description,
    author="Ryan McGuire, Doug Latornell, and the Blogofile Contributors",
    author_email="blogofile-discuss@googlegroups.com",
    url="http://www.blogofile.com",
    license="MIT",
    classifiers=classifiers,
    packages=["blogofile_blog"],
    package_data=find_package_data("blogofile_blog", "site_src"),
    include_package_data=True,
    install_requires=dependencies,
    zip_safe=False,
    entry_points={
        "blogofile.plugins": ["blogofile_blog = blogofile_blog"]},
)
