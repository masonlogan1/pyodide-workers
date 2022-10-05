"""When imported, this module will create and register a javascript module to server as the foundation for making
web requests"""
import logging
import os

from importlib import import_module
from importlib.util import find_spec

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# When loaded into Pyodide these will be functional, but otherwise the compatibility classes are needed.
# This is mostly used for running the unit tests and doing local development work
try:
    import js
except ModuleNotFoundError as e:
    from pywebworker.pyodide_compatibility import js
try:
    import pyodide_js
except ModuleNotFoundError as e:
    from pywebworker.pyodide_compatibility import pyodide_js
try:
    from pyodide.code import run_js
except ModuleNotFoundError as e:
    from pywebworker.pyodide_compatibility import run_js


# TODO: find programmatic way to import pyodide-specific modules/compatibility modules
#pyodide_modules = ['js', 'pyodide_js', 'pyodide.code']
#for module in pyodide_modules:
#    # since these modules only exist in pyodide, we import their compatibility version if they are unavailable
#    if not find_spec(module):
#        logger.warning(f'MODULE "{module}" UNAVAILABLE, USING COMPATABILITY WRAPPER')
#        globals()[module] = getattr(import_module('pywebworker.pyodide_compatibility', package='pywebworker'), module)
#    else:
#        import_module(module)


def setup_worker_js() -> str:
    """
    Returns JavaScript that can be executed to create the Python-JavaScript Worker objects
    :return: executable js code
    """
    with open(os.path.abspath(os.path.dirname(__file__))+'/worker.js', 'r') as reader:
        script = ''.join(reader.readlines())
    return script


def get_pyworker_js() -> str:
    """
    Returns JavaScript that can be run in a web worker thread to allow python code passed via event messages to be
    executed and the results returned
    :return: executable js code
    """
    with open(os.path.abspath(os.path.dirname(__file__))+'/pyworker.js', 'r') as reader:
        script = ''.join(reader.readlines())
    return script


# this will be run when the module is imported. Pyodide-specific code is kept here
def setup():
    js.load_to_pyodide = pyodide_js.registerJsModule
    run_js(setup_worker_js() + "\nload_to_pyodide('pywebworker_js', new_worker);")


setup()


def WORKER_OBJ(script):
    """
    Convenience for allowing consumers of the javascript object to no longer need to directly import the class
    registered by pyodide
    :param script: the script to be provided to the web worker
    :return: webworker javascript object
    """
    if find_spec('pywebworker_js'):
        import pywebworker_js
    else:
        logger.warning(f'MODULE "pywebworker_js" UNAVAILABLE, USING COMPATABILITY WRAPPER')
        from pywebworker.pyodide_compatibility import pywebworker_js
    return pywebworker_js(script)

PYWORKER_SCRIPT = get_pyworker_js()
