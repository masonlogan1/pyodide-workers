from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as reader:
    long_description = '\n'.join(reader.readlines())

VERSION = '0.0.8'
DESCRIPTION = 'Python tools for interacting with Web Workers in Pyodide'
LONG_DESCRIPTION = long_description

# Setting up
# noinspection SpellCheckingInspection
setup(
    name="pywebworker",
    version=VERSION,
    author="malogan (Mason Logan)",
    author_email="<dev@masonlogan.com>",
    url='https://github.com/masonlogan1/pywebworker',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    data_files=[('js', ['pywebworker/worker.js', 'pywebworker/pyworker.js'])],
    include_package_data=True,
    keywords=['python', 'pyodide', 'web workers', 'web api'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
