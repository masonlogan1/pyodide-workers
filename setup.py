from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.5'
DESCRIPTION = 'Python tools for interacting with Web Workers in Pyodide'
LONG_DESCRIPTION = 'A package that wraps generic JavaScript with Python classes to allow for the easy use of the Web ' \
                   'Worker API in Pyodide Projects'

# Setting up
setup(
    name="pywebworker",
    version=VERSION,
    author="malogan (Mason Logan)",
    author_email="<masonlogan1@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'pyodide', 'web workers', 'web api'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)