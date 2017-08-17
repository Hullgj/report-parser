try:
    from setuptools import setup
except ImportError:
    from distutils.core import setuptools

config = [
    'description': 'Report Parser for JSON',
    'author': 'Gavin Hull',
    'url': 'none',
    'download_url': 'none',
    'author_email': 'gjh9@kent.ac.uk',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['report_parser'],
    'name': 'report_parser'
]

setup(**config)