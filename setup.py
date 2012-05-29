# -*- coding: utf-8 -*-
import os.path
import re
import sys
from setuptools import setup
import blogofile_blog


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

description = blogofile_blog.__dist__['pypi_description']
with open('CHANGES.txt', 'rt') as changes:
    long_description = description + '\n\n' + changes.read()

dependencies = ['argparse'] if PY26 else []


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
    'Natural Language ::  English',
])

setup(
    name="blogofile_blog",
    version=blogofile_blog.__version__,
    description=blogofile_blog.__dist__['pypi_description'],
    long_description=long_description,
    author=blogofile_blog.__dist__["author"],
    author_email="blogofile-discuss@googlegroups.com",
    url=blogofile_blog.__dist__["url"],
    license="MIT",
    classifiers=classifiers,
    packages=["blogofile_blog"],
    package_data=find_package_data("blogofile_blog", "site_src"),
    include_package_data=True,
    install_requires=dependencies,
    entry_points={
        "blogofile.plugins": ["blogofile_blog = blogofile_blog"]},
)
