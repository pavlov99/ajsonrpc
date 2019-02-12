import pytest

from ..core import JSONRPC20Request
from ..manager import AsyncJSONRPCResponseManager


async def async_fun():
    return 'async function'


class TestJSONRPCResponseManager:
    dispatcher = {
        "add": sum,
        "multiply": lambda a, b: a * b,
        "list_len": len,
        "101_base": lambda **kwargs: int("101", **kwargs),
        "key_error": lambda: raise_(KeyError("error_explanation")),
        "type_error": lambda: raise_(TypeError("TypeError inside method")),
        "async_fun": async_fun,
    }
    manager = AsyncJSONRPCResponseManager(dispatcher=dispatcher)

    @pytest.mark.asyncio
    async def test_handle_request(self):
        req = JSONRPC20Request('add', params=[[1, 2]], id=0)
        res = await self.manager.handle_request(req)
        assert res.result == 3