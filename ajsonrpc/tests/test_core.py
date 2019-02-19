import pytest

from ..core import JSONRPC20Request


class TestJSONRPC20Request:

    request_params = {
        "method": "add",
        "params": [1, 2],
        "id": 1,
    }

    def test_correct_init(self):
        JSONRPC20Request(**self.request_params)

    def test_validation_incorrect_no_parameters(self):
        with pytest.raises(TypeError):
            JSONRPC20Request()

    def test_default_not_notification(self):
        r = JSONRPC20Request(method='echo')
        assert not r.is_notification
