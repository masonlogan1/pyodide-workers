/** worker.js
 *  Provides classes for Web Workers so PyWebWorker's Python objects can have better interaction with them.
 *
 ** ======== ======== ======== ======== ======== ======== ======== ======== */

WorkerException = class extends Error {
  constructor(message){
      super(message);
      this.name = this.constructor.name;
  }
}

/**
 * @constructor
 * @type WebWorker
 * @param {string} script the script to be run in the web worker
 */
class WebWorker {

  DATA_URI_PREFIX = 'data:text/javascript,'
  messages = [];
  state = 'Ready';
  id = window.performance.now().toString()+ (Math.random()*10000000).toFixed();

  constructor(script){
      this.script = script;
  }

  start(){
      /**
       * Creates the Worker object and begins running the parallel thread
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
      /**
       * @param {string} newScript Replaces the script stored in the object
       */
      // TODO: throw exception when the worker is running; script cannot be changed after
      this.script = newScript
  }

  get_script(){
      /**
       * @type {string}
       * @return {string} the script currently running/to be run
       */
      return this.script
  }

  get_state(){
      /**
       * @return {string} the state of the worker
       */
      return this.state;
  }

  get_id(){
      /**
       * @return {string} the unique ID for this worker
       */
      return this.id;
  }

  get_messages(){
      /**
       * @return {Array<Event>} all messages received from the worker
       */
      return this.messages;
  }

  send_message(message){
      /**
       * @param {Object}
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
}

// provides an easy way for Python to create new objects
new_worker = (script) => {return new WebWorker(script)}