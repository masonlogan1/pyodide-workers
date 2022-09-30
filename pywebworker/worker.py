import logging

from queue import Queue

# this module is registered in worker_config.py
from pywebworker import worker_config
import pywebworker_js
import js


DEFAULT_LOG_LEVEL = logging.DEBUG
# default logger
logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LOG_LEVEL)


class WorkerError(Exception):
    def __init__(self, message, *args):
        """
        :param message: details to display in error message

        Generic exception for Worker objects.
        """
        super().__init__(args)
        self.message = message

    def __str__(self):
        return f'Error with worker thread: {self.message}'


class FatalWorkerError(WorkerError):
    def __init__(self, message, worker, *args):
        """
        :param message: details to display in error message
        :param worker: worker to kill

        Exception for worker objects that kills the worker
        """
        super().__init__(args)
        self.message = message
        worker.kill()

    def __str__(self):
        return f'WORKER TERMINATED - FATAL ERROR WITH WORKER THREAD: {self.message}'


class WorkerMessage:
    """Message from a PyWorker web pywebworker"""
    def __init__(self, data, status=False):
        # TODO: add datetime for when message was sent
        self.data = data
        self.status = status

    def read(self):
        self.status = True
        return self.data

    def is_read(self) -> bool:
        return self.status


class WorkerMessageQueue:
    """
    Queue that converts web worker events into WorkerMessage objects before queueing for user collection
    """
    def __init__(self):
        self.queue = Queue()

    def put(self, event):
        """
        :param event: web worker event
        Converts a web worker event into a WorkerMessage and puts it into a queue
        """
        self.queue.put(WorkerMessage(event.data))

    def get(self, block=True, timeout=None) -> WorkerMessage:
        """
        :param block: whether to wait for the next message
        :param timeout: time to wait for the next message, if applicable
        :return: the next WorkerMessage in the queue
        """
        return self.queue.get(block=block, timeout=timeout)


# You may be asking "couldn't you just use pyodide's js module for this?" The short answer is kinda, the long answer
# is yes, but with a lot more difficulty. Passing messages back and forth can be buggy and in some cases they can be
# missed. The Worker class wraps a JavaScript object that helps to facilitate stable communication for any inheriting
# classes
class Worker:
    """
    Creates a browser-friendly, pythonic way of using web workers with pyodide
    """
    def __init__(self, script, queue=None, loglevel=logging.DEBUG):
        self.logger = logging.getLogger('PyWorker')
        self.logger.setLevel(loglevel)

        self.script = script
        self.worker = pywebworker_js(script)

        self.queue = queue
        self.messages = list()

    def get_unread_messages(self) -> list[WorkerMessage]:
        """adds any missing messages to the message repository and returns anything not marked as opened"""
        return [message for message in self.messages if not message.is_read()]

    def has_unread_messages(self) -> bool:
        """
        Returns True if there are any unread messages
        """
        return any([not message.is_read() for message in self.messages])

    def get_message(self, index) -> WorkerMessage:
        """
        Returns the message at the index
        """
        return self.messages[index]

    def get_messages(self) -> list[WorkerMessage]:
        """
        :return: list of messages
        """
        # TODO: add ability to filter messages by time recieved
        return self.messages

    def get_next_unread_message(self) -> WorkerMessage:
        """
        :return: the next unread message from the list, if one exists
        Provides the next unread message. If one does not exist, returns None
        """
        # TODO: get_next_unread_message() should return next unread message from the list
        raise NotImplementedError

    def get_queue(self) -> WorkerMessageQueue:
        """
        :return: the queue of messages coming from the web worker, if applicable
        Provides the raw message queue
        """
        return self.queue

    def get_next_from_queue(self, block=False, timeout=None):
        """
        :param block: whether to wait for a message to come in, defaults False
        :param timeout: seconds to wait for a message if blocking
        :return: next message, if available
        Returns the next message if one is available. Does not block by default; unintentionally blocking can place
        entire interpreter and possibly webpage into a deadlock. Use carefully!
        """
        return self.queue.get(block=block, timeout=timeout)

    def send_message(self, message) -> None:
        """
        Sends a message to the pywebworker
        """
        if self.worker.get_state() == 'Running':
            self.worker.send_message(message)
        else:
            raise WorkerError('Worker is not running; cannot send messages to inactive workers')

    def get_id(self) -> str:
        """
        Returns the unique id value for this pywebworker
        """
        return self.worker.get_id()

    def get_script(self) -> str:
        return self.worker.get_script()

    def set_script(self, script) -> None:
        """
        :param script: the new script to use
        Sets the script for the worker. Must be set before starting, script cannot be changed once in progress
        """
        if self.worker.get_state() != 'Running':
            return self.worker.set_script(script)
        else:
            raise WorkerError('Cannot change script after starting!')

    def onmessage(self, event) -> None:
        """
        :param event: message event from the web worker
        Populates the messages and queue (if provided) with incoming messages whenever one is sent. This method is
        event-driven and will automatically populate the messages. Must be set BEFORE running if overriding or it will
        not be picked up by the module.
        """
        if self.queue:
            self.queue.put(event)
        self.messages.append(WorkerMessage(event.data))

    def start(self) -> str:
        """
        Starts the web pywebworker and the message listening service
        """
        self.worker.start()
        self.worker.pywebworker.onmessage = lambda event: self.onmessage(event)
        return self.worker.get_id()

    def kill(self) -> None:
        """
        Terminates the web pywebworker. This action is immediate, anything in-progress will be abruptly stopped
        """
        self.worker.kill()

    def __del__(self):
        try:
            self.kill()
        except Exception as e:
            # Currently we just discard all exceptions, the goal is really just to execute the kill command so threads
            # aren't lost to the void
            pass