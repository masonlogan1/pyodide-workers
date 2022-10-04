"""When imported, this module will create and register a javascript module to server as the foundation for making
web requests"""
import os
import js
import pyodide_js
from pyodide.code import run_js


def setup_worker_js() -> str:
    """
    Returns JavaScript that can be executed to create the Python-JavaScript Worker objects
    :return: executable js code
    """
    with open(os.path.abspath(os.path.dirname(__file__))+'/worker.js', 'r') as reader:
        js = ''.join(reader.readlines())
    return js


def get_pyworker_js() -> str:
    """
    Returns JavaScript that can be run in a web worker thread to allow python code passed via event messages to be
    executed and the results returned
    :return: executable js code
    """
    with open(os.path.abspath(os.path.dirname(__file__))+'/pyworker.js', 'r') as reader:
        js = ''.join(reader.readlines())
    return js


# this will be run when the module is imported
def setup():
    js.load_to_pyodide = pyodide_js.registerJsModule
    run_js(setup_worker_js() + "\nload_to_pyodide('pywebworker_js', new_worker);")


setup()
import pywebworker_js


def WORKER_OBJ(script):
    """
    Convenience for allowing consumers of the javascript object to no longer need to directly import the class
    registered by pyodide
    :param script: the script to be provided to the web worker
    :return: webworker javascript object
    """
    return pywebworker_js(script)

PYWORKER_SCRIPT = get_pyworker_js()
