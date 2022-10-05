class __dummy_class:
    def __init__(self, name=None, *args, **kwargs):
        self.name = name
        self.args = args
        [setattr(self, key, value) for key, value in kwargs.items()]
    def __doc__(self):
        return f"""Dummy class for {'module' if not self.name else self.name} (doesn't exist outside Pyodide)"""

def __dummy_function(*args, **kwargs):
    """Dummy function (real does not exist outside of Pyodide)"""
    # if a function is supplied as keyword argument 'f' it will execute something, otherwise returns None
    return kwargs.get('f', lambda *args, **kwargs: None)(*args, **kwargs)

js = __dummy_class(name='js', load_to_pyodide='load_to_pyodide')
pyodide_js = __dummy_class(name='pyodide_js', registerJsModule='registerJsModule')
run_js = __dummy_function

pywebworker_js = __dummy_class(name='pywebworker_js')
