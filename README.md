# PyWebWorker

## Background
Out-of-the box Pyodide lacks support for a pure Python solution to using web workers. PyWebWorker seeks to fill that 
gap by providing a set of Python objects and functions to interact with the Web Worker API.

## Installation
PyWebWorker can be imported using **micropip**:

```python
import micropip
await micropip.install('pywebworker')
```

## Quick Reference
The examples here are valid as of **Version 0.0.6**

```python
from pywebworker.worker import PyWorker

# This script will print a message to the console when the worker starts and
# will echo back any messages it receives
script = '''
console.log('worker created');
self.onmessage = function(message){
	console.log('Received: ' + message.data);
	self.postMessage(message.data);
}
'''

worker = PyWorker(script)
worker.start()

# the script echos back whatever we send, that message should be ready for us
worker.send_message('This is the first message')
messages = worker.get_unread_messages()

# messages have a .read method so the consumer knows what has and has not been processed
print([message.read() for message in messages])

# the message list can be checked for any unread messages using the has_unread_messages method
worker.send_message('This is the second message')
print(worker.has_unread_messages())

# individual messages can be checked to see if they have been read or not
first_message = worker.get_message(0)
second_message = worker.get_message(1)
print(first_message.is_opened())
print(second_message.is_opened())

# this isn't recommended, but if you really need to check for new messages without using has_unread_messages() or
# get_unread_messages(), _update_messages() will update the messages attribute.
# PLEASE NOTE THAT THIS IS A TEMPORARY WAY TO UPDATE THE LIST, THIS WILL BE REMOVED LATER
worker.send_message('This is the third message')
worker._update_messages()
print(worker.get_message(2).read())

# killing the worker stops it *immediately*. Anything in-progress will be stopped, so only use this when it is certain
# the worker is done and no longer needed!
worker.kill()
```

## Roadmap

#### *This timeline is tentative and subject to change*

### Version 0.1.0

- PyWorker and JsWorker as objects that run either Python or JavaScript, respectively
- Exception handling for common errors
- Message queues for inbound/outbound messages to the worker
- Enhancements to underlying JavaScript
- Add tests for basic object functions

### Version 0.2.0

- Ability to execute scripts from Enscriptem and URI's
- Place JavaScript for underlying JS objects into its own file (as opposed to text in a python module)

### Version 0.X.0: Planned near-future but not scheduled

- Ability to pass environment settings to the interpreter in PyWorkers (currently runs on defaults)
- Creation of flexible thread pool for PyWorkers

## Known Limitations

### PyWorkers are slow to start
In order to run Pyodide in a worker, it must be downloaded and started in each worker thread, which takes time. The 
goal is to eventually have a pool of threads that start this process in the background on import.