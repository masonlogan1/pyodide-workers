// find the output element
const output = document.getElementById("output");

let pyodideReadyPromise = null;

// IMPORTANT: This variable MUST be present! It will allow access to the pyodide object for ANY js execution in-scope
// which is necessary for the web workers
//let pyodide = null;

// TODO: This script needs refactoring for readability and maintainability

// initialize codemirror and pass configuration to support Python and the dracula theme
const editor = CodeMirror.fromTextArea(
    document.getElementById("code"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false,
        },
        theme: "dracula",
        lineNumbers: true,
        indentUnit: 4,
        matchBrackets: true,
    }
);

// add pyodide returned value to the output
function addToOutput(stdout) {
    output.value += ">>> " + stdout + "\n";
}

// clean the output section
function clearHistory() {
    output.value = "";
}

// init pyodide and show sys.version when it's loaded successfully
async function setup() {
    let pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/",
    });
    version = pyodide.runPython(`
    import platform
    import sys
    platform.python_version()
  `);

    console.log('Loading micropip...')
    await pyodide.loadPackage("micropip");

    output.value = "Python "+ version + " Ready" + "\n\n";

    return pyodide;
}

async function set_pyodide(){
    console.log('Setting up pyodide instance...')
    //pyodide = await pyodideReadyPromise;
}

// pass the editor value to the pyodide.runPython function and show the result in the output section
async function evaluatePython() {
    let pyodide = await pyodideReadyPromise;
    try {
        pyodide.runPython(`
          import io
          sys.stdout = io.StringIO()`);
        let result = await pyodide.runPythonAsync(editor.getValue());
        let stdout = await pyodide.runPythonAsync("sys.stdout.getvalue()");
        addToOutput(stdout);
    } catch (err) {
        addToOutput(err);
    }
}

async function reset() {
    document.getElementById('runButton').disabled = true;
    clearHistory();
    let message = 'Resetting the environment...\n';
    output.value = message;
    pyodideReadyPromise = setup();
    await set_pyodide();
    document.getElementById('runButton').disabled = false;
}

// This is the text that will be loaded into the editor
const python_script = `import micropip
await micropip.install('pywebworker')
from pywebworker import Worker

# this is the script that will be loaded into the worker
script = '''
console.log('worker created');
self.onmessage = function(message){
    console.log('Received: ' + message.data);
    self.postMessage(message.data);
}
'''

# create the worker by passing in a script as a string
worker = Worker(script)
worker.start()

# check the browser console, you should see 'worker created'`

async function main(){
    output.value = "Initializing...\n";
    editor.setValue('Initializing...')
    document.getElementById('runButton').disabled = true;
    document.getElementById('code').readOnly = true;
    pyodideReadyPromise = setup();
    await set_pyodide()
    editor.setValue(python_script);
    document.getElementById('runButton').disabled = false;
    document.getElementById('code').readOnly = false;
}
main()

