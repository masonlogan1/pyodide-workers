importScripts('https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js');
let pyodideReadyPromise = null;

/**
 * Loads the Pyodide package and micropip to allow Python execution in the worker thread
 * @returns {Promise<*>}
 */
async function setup() {
    console.debug("Loading pyodide in worker thread");
    let pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/",
    });
    console.log('Setting up std_out...');
    await pyodide.runPythonAsync('import io;import sys;sys.stdout = io.StringIO()');
    console.log('Loading micropip...');
    await pyodide.loadPackage('micropip');
    console.debug('Python Ready');
    return pyodide;
}

/**
 * Executes a provided Python statement
 * @param {string} code the code to be executed
 * @returns {Promise<string>} the standard-out result from execution
 */
async function execute_python(code){
	let pyodide = await pyodideReadyPromise;
	console.debug('executing received python statement');
    let execution = await pyodide.runPythonAsync(code);
    let stdout = await pyodide.runPythonAsync('sys.stdout.getvalue()');
    self.postMessage(stdout);
    let reset = await pyodide.runPythonAsync('sys.stdout = io.StringIO()');
    return stdout;
}

/**
 * Performs setup operations and sets the globally-scoped pyodideReadyPromise variable
 * @returns {Promise<void>}
 */
async function main(){
    pyodideReadyPromise = setup();
}
main();

self.onmessage = async function (message) {
    /**
     * @type {any} MessageEvent containing a Python command
     * Executes python statements passed in as MessageEvents
     */
    /* TODO: add ability to distinguish message types by passing dict objects as {type:str, content:str} */
    await execute_python(message.data);
}
