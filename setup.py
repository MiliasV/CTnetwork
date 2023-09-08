from setuptools import find_packages, setup


# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


# This call to setup() does all the work
setup(
    name='ctstreets',
    packages=find_packages(include=['ctstreets']),
    version='0.1.0',
    description='First Demo iteration',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Vasileios Milias',
    author_email='v.milias@tudelft.nl',
    classifiers=[
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Operating System :: OS Independent"
],
    license='tbd',
    install_requires=['networkx','osmnx','pandas','geopandas','igraph', 'shapely', 'numpy','osm2geojson'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
