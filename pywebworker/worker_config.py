"""When imported, this module will create and register a javascript module to server as the foundation for making
web requests"""
# NOTE: YOU MUST HAVE THE PYODIDE OBJECT AVAILABLE AS A GLOBAL VARIABLE IN JAVASCRIPT NAMED "pyodide". AS OF RIGHT NOW,
# THIS IS THE ONLY THING NEEDED ON THE END

SETUP_JS = '''
WorkerException = class extends Error {
  constructor(message){
      super(message);
      this.name = this.constructor.name;
  }
}

WebWorker = class {

  DATA_URI_PREFIX = 'data:text/javascript,'

  messages = [];
  state = 'Ready';
  id = window.performance.now().toString()+ (Math.random()*10000000).toFixed();

  constructor(script){
      this.script = script;
  }

  start(){
      /*
      Starts a pywebworker thread using a data URI
      */
      if (this.state === 'Running'){
          throw new WorkerException('Cannot start ' + this.id +', pywebworker is already running');
      }
      this.pywebworker = new Worker(this.DATA_URI_PREFIX + this.script);
      this.pywebworker.onmessage = (event) => {
          this.messages[this.messages.length] = event;
      }
      this.state = 'Running';
  }

  set_script(newScript){
      /*
      sets the existing script to a new script value
      */
      this.script = newScript
  }

  get_script(){
      return this.script
  }

  get_state(){
      /*
      returns the state of the instance
      */
      return this.state;
  }

  get_id(){
      /*
      returns the ID of the instance
      */
      return this.id;
  }

  get_messages(){
      /*
      returns the most recent message from the pywebworker
      */
      return this.messages;
  }

  send_message(message){
      /*
      sends a message to the pywebworker via the postMessage method
      */
      this.pywebworker.postMessage(message);
  }

  kill() {
      /*
      kills the pywebworker thread
      */
      if (this.state !== 'Running'){
          throw new WorkerException('Cannot terminate ' + this.id +', pywebworker is not running');
      }
      this.pywebworker.terminate()
  }

  static create_worker(script) {
      /*
      Creates a new PyWorker object with the provided script
      */
      console.debug('creating new PyWorker');
      return new WebWorker(script);
  }
}
pyodide.registerJsModule('webworker', WebWorker);'''


# this will be run when the module is imported
def setup():
    from pyodide.code import run_js
    run_js(SETUP_JS)


setup()
