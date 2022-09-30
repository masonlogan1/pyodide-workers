"""When imported, this module will create and register a javascript module to server as the foundation for making
web requests"""
import os
import js
import pyodide_js
from pyodide.code import run_js

def get_worker_js():
    with open(os.path.abspath(os.path.dirname(__file__))+'/worker.js', 'r') as reader:
        js = ''.join(reader.readlines())
    return js


# this will be run when the module is imported
def setup():
    js.load_to_pyodide = pyodide_js.registerJsModule
    run_js(get_worker_js() + "\nload_to_pyodide('pywebworker_js', new_worker);")

setup()
