try:
    from setuptools import setup
    from setuptools.command.build_py import build_py
except ImportError:
    from distutils.core import setuptools
    from distutils.command.build import build

class NPMInstall(build):
    def run(self):
        self.run_command("npm install casperjs phantomjs")
        build.run(self)

config = {
    'description': 'RanDep Ransomware Deployment Classifier',
    'author': 'Gavin Hull',
    'url': 'https://github.com/Hullgj/report-parser/blob/master/report_parser',
    'download_url': 'https://github.com/Hullgj/report-parser.git',
    'author_email': 'gjh9@kent.ac.uk',
    'version': '0.1',
    'install_requires': ['nose', 'plotly'],
    'packages': ['report_parser'],
    'name': 'report_parser',
    'cmdclass' : {
        'npm_install': NPMInstall
    },
}

setup(**config)