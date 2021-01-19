"""Test Async JSON-RPC Response manager."""
import unittest

from ..core import JSONRPC20Request, JSONRPC20Response, JSONRPC20MethodNotFound
from ..manager import AsyncJSONRPCResponseManager


def subtract(minuend, subtrahend):
    return minuend - subtrahend

async def async_fun():
    return 'async function'


class TestAsyncJSONRPCResponseManager(unittest.IsolatedAsyncioTestCase):

    dispatcher = {
        "add": sum,
        "multiply": lambda a, b: a * b,
        "subtract": subtract,
    }

    manager = AsyncJSONRPCResponseManager(dispatcher=dispatcher)

    async def test_get_request_method_not_found(self):
        req = JSONRPC20Request('does_not_exist', id=0)
        res = await self.manager.get_response(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error, JSONRPC20MethodNotFound())
        self.assertEqual(res.id, req.id)

    async def test_test_get_request_method_not_found_notification(self):
        req = JSONRPC20Request('does_not_exist', is_notification=True)
        res = await self.manager.get_response(req)
        self.assertIsNone(res)
