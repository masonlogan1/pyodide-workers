import logging

from pywebworker.worker import Worker, WorkerMessage, WorkerMessageQueue, WorkerError
from pywebworker.worker_config import PYWORKER_SCRIPT

class PyWorker(Worker):
    def __init__(self, onmessage_actions=None, loglevel=logging.DEBUG):
        super().__init__(PYWORKER_SCRIPT, onmessage_actions=onmessage_actions, loglevel=loglevel)