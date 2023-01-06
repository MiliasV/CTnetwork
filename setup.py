from setuptools import find_packages, setup


setup(
    name='ctwalk',
    packages=find_packages(include=['ctwalk']),
    version='0.1.0',
    description='First iteration',
    author='Vasileios Milias',
    license='tbd',
    install_requires=['networkx','osmnx','pandas','geopandas','igraph', 'shapely', 'numpy'],
    setup_requires=[],
    tests_require=[],
    test_suite='tests',
)
