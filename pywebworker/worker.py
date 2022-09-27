import logging
import pywebworker.worker_config
import webworker


DEFAULT_LOG_LEVEL = logging.DEBUG


class PyWorkerMessage:
    """Message from a PyWorker web pywebworker"""
    def __init__(self, data, read):
        self.data = data
        self.opened = False

    def read(self):
        self.opened = True
        return self.data

    def is_opened(self):
        return self.opened


class PyWorker:
    """
    Creates a browser-friendly, pythonic way of using web workers with pyodide
    """
    def __init__(self, script, loglevel=logging.DEBUG):
        self.logger = logging.getLogger('PyWorker')
        self.logger.setLevel(loglevel)

        self.script = script
        self.worker = webworker.create_worker(script)

        self.messages = list()

    def _update_messages(self):
        self.messages += [PyWorkerMessage(msg.data, False)
                          for msg in self.worker.get_messages()[len(self.messages):]]

    def get_unread_messages(self):
        """adds any missing messages to the message repository and returns anything not marked as opened"""
        self._update_messages()
        return [message for message in self.messages if not message.is_opened()]

    def has_unread_messages(self):
        """
        Returns True if there are any unread messages
        """
        self._update_messages()
        return any([not message.is_opened for message in self.messages])

    def get_message(self, index):
        """
        Returns the message at the index
        """
        return self.messages[index]

    def send_message(self, message):
        """
        Sends a message to the pywebworker
        """
        self.worker.send_message(message)

    def get_id(self):
        """
        Returns the unique id value for this pywebworker
        """
        return self.worker.get_id()

    def get_script(self):
        return self.worker.get_script()

    def set_script(self):
        return self.worker.set_script()

    def start(self):
        """
        Starts the web pywebworker and the message listening service
        """
        self.worker.start()

    def kill(self):
        """
        Terminates the web pywebworker. This action is immediate, anything in-progress will be abruptly stopped
        """
        self.worker.kill()

script = '''console.log('pywebworker created');
self.onmessage = function(message){
    console.log('Received: ' + message.data);
    self.postMessage(message.data);
}'''
