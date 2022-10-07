import unittest

from unittest.mock import MagicMock, patch, call

from pywebworker import worker


class MockMessageEvent:
    """Mocks MessageEvent from javascript"""
    def __init__(self, **kwargs):
        mandatory_fields = [('data', ''), ('origin', ''), ('lastEventId', '0'), ('source', ''), ('ports', list())]
        # sets up mandatory fields as well as any additional kwarg values as object attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        for key, value in [field for field in mandatory_fields if field[0] not in kwargs.keys()]:
            setattr(self, key, value)


class MockWebWorker(MagicMock):
    """Mocks functionality of a web worker. Can take a script, receive messages, and generates a message or list of
    messages. Parameter 'script' will perform the function on incoming messages before returning. Will
    echo back whatever is received by default."""
    def __init__(self, script=None):
        super().__init__()
        # IMPORTANT NOTE: We cannot run javascript in python unit tests! While it would be ideal to run these tests
        # with actual javascript, the provided scripts MUST BE PYTHON SCRIPTS! The functionality is identical otherwise
        self.script = script if script else lambda x: {'data': x}

        # onmessage has to be set by the consumer. If it is not set, nothing is done
        self.onmessage = lambda x: None

    def postMessage(self, message):
        """processes the message and passes the output in MessageEvent format to onmessage"""
        # performs the defined function (if provided) and converts to MessageEvent format
        response = self._message_to_message_event(**self.script(message))
        # passes the MessageEvent-formatted object to the onmessage function (if applicable)
        self.onmessage(response)

    def _message_to_message_event(self, **kwargs):
        """takes the incoming args and creates a MockMessageEvent from them"""
        return MockMessageEvent(**kwargs)


class MockWorkerObj(MagicMock):
    """Mocks functionality of WORKER_OBJ from worker_config. Underlying object is wrapped javascript; useful tests
    require a native python object. This object mimics the function of the javascript object"""

    def __init__(self, script, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script = script
        self.messages = list()
        self.DATA_URI_PREFIX = 'data:text/javascript,'
        self.state = 'Ready'
        self.id = '00000001'

    def start(self):
        self.webworker = MockWebWorker()
        self.webworker.status = 'Running'
        self.webworker.onmessage = lambda event: self.messages.append(event)

    def set_script(self, newScript):
        self.script = newScript

    def get_script(self):
        return self.script

    def get_state(self):
        return self.state

    def get_id(self):
        return self.id

    def get_messages(self):
        return self.messages

    def send_message(self, message):
        self.webworker.postMessage(message)

    def kill(self):
        pass


@patch.object(worker, 'WORKER_OBJ', side_effect=lambda script: MockWorkerObj(script))
class MyTestCase(unittest.TestCase):
    """Tests the various methods and attributes of the Worker class"""
    # NOTE: These tests suffer from the limitation that they must be run without Pyodide or the ability to use
    # JavaScript web workers. Good unit tests of the wrapper class should be mocking the actual object anyway, but
    # it is possible some functionality may slip through the cracks due to this limitation.

    def test_create_new_worker(self, mock_worker_obj):
        """Tests that a Worker object passes the correct script to the underlying Object"""
        sample_script = 'script'

        expected_state = 'Ready'
        expected_prefix = 'data:text/javascript,'

        test_worker = worker.Worker(sample_script)

        # checks that the script was set as an attribute
        self.assertEqual(sample_script, test_worker.script)

        # checks that the script was sent to the javascript object
        mock_worker_obj.assert_has_calls([call(sample_script)])

    def test_create_new_worker_with_single_onmessage_action(self, mock_worker_obj):
        """Tests that a Worker object properly sets a single onmessage_action"""
        sample_script = 'script'

        action_0 = lambda event: event

        sample_actions = [action_0]

        test_worker = worker.Worker(sample_script, onmessage_actions=sample_actions)

        self.assertEqual(sample_actions, test_worker.get_onmessage())

    def test_create_new_worker_with_multiple_onmessage_actions(self, mock_worker_obj):
        """Tests that a Worker object properly sets multiple onmessage_actions"""
        sample_script = 'script'

        action_0 = lambda event: event
        action_1 = lambda event: event
        action_2 = lambda event: event

        sample_actions = [action_0, action_1, action_2]

        test_worker = worker.Worker(sample_script, onmessage_actions=sample_actions)

        self.assertEqual(sample_actions, test_worker.get_onmessage())

    def test_get_onmessage(self, mock_worker_obj):
        """Tests that get_onmessage returns the full list of onmessage functions, excluding the built-in message
        handler"""
        sample_script = 'script'

        action_0 = lambda event: event
        action_1 = lambda event: event
        sample_actions = [action_0, action_1]

        test_worker = worker.Worker(sample_script)
        # manually sets the onmessage actions
        test_worker._Worker__onmessage_actions = sample_actions

        self.assertEqual(test_worker.get_onmessage(), sample_actions)

    def test_add_to_onmessage_single_function(self, mock_worker_obj):
        """Tests that the add_to_onmessage function adds a single function when passed"""
        sample_script = 'script'

        action_0 = lambda event: event

        test_worker = worker.Worker(sample_script)
        test_worker.add_to_onmessage(action_0)

        self.assertEqual([action_0], test_worker.get_onmessage())


if __name__ == '__main__':
    unittest.main()
