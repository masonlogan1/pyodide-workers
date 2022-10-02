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
The examples here are valid as of **Version 0.0.8**

### Sending/Receiving with built-in messaging
```python
from pywebworker import Worker

# This script will print a message to the console when the worker starts and
# will echo back any messages it receives
script = '''
console.log('worker created');
self.onmessage = function(message){
	console.log('Received: ' + message.data);
	self.postMessage(message.data);
}
'''

# IMPORTANT NOTE: executing this whole script will yield errors! Because the worker executes in another thread, this
# script will go to the next line IMMEDIATELY after sending a message. The workers, while very fast, cannot echo the 
# messages back that quickly.
worker = Worker(script)
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
print(first_message.is_read())
print(second_message.is_read())

# messages can be directly requested as well
worker.send_message('This is the third message')
print(worker.get_message(2).read())

# you can also get the next unread message:
worker.send_message('This is the fourth message')
print(worker.get_next_unread_message().read())

# killing the worker stops it *immediately*. Anything in-progress will be stopped, so only use this when it is certain
# the worker is done and no longer needed!
worker.kill()
```

### Sending/Receiving with custom onmessage process
```python
from pywebworker import Worker, WorkerMessageQueue

# sample script for quick testing
sample_script = '''
console.log('worker created');
self.onmessage = function(message){
    console.log('Received: ' + message.data);
    self.postMessage(message.data);
}
'''

# WorkerMessageQueue objects are provided to more easily convert JavaScript's EventMessage objects into more
# python-friendly WorkerMessage objects, but any function can be given to onmessage
message_queue = WorkerMessageQueue()
queue_method = lambda event: message_queue.put(event)
worker = Worker(sample_script, [queue_method])
worker.start()

# Functions can also be added to the onmessage execution process after the worker is created
#worker.add_to_onmessage(lambda event: message_queue.put(event))

# Reminder: executing this entire block at once will cause an error; the worker cannot echo as fast as pyodide moves
# to the next line
worker.send_message('message 0')
print(worker.messages)
queue_message = message_queue.get()
print(queue_message.read())
```

### Sending/Receiving using Python code
```python
from pywebworker import PyWorker

# PyWorkers can take time to load! Give it a few seconds to get running before expecting the output
worker = PyWorker()
worker.start()

# whatever is passed via send_message is executed!
worker.send_message("print('hello world')")
print(worker.get_next_unread_message().read())
```


## Roadmap

#### *This timeline is tentative and subject to change*

### Version 0.1.0

- PyWorker and JsWorker as objects that run either Python or JavaScript, respectively
- Exception handling for common errors
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