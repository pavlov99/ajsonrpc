"""Test Async JSON-RPC Response manager."""
import unittest

from ..core import JSONRPC20Request, JSONRPC20Response, JSONRPC20MethodNotFound, JSONRPC20InvalidParams, JSONRPC20ServerError, JSONRPC20DispatchException
from ..manager import AsyncJSONRPCResponseManager


class TestAsyncJSONRPCResponseManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        def subtract(minuend, subtrahend):
            return minuend - subtrahend

        def raise_(e: Exception):
            raise e

        async def async_sum(*args):
            return sum(args)

        self.dispatcher = {
            "subtract": subtract,
            "async_sum": async_sum,
            "dispatch_exception": lambda: raise_(
                JSONRPC20DispatchException(
                    code=4000, message="error", data={"param": 1}
                )
            ),
            "unexpected_exception": lambda: raise_(ValueError("Unexpected")),
        }

        self.manager = AsyncJSONRPCResponseManager(dispatcher=self.dispatcher)

    async def test_get_response(self):
        req = JSONRPC20Request("subtract", params=[5, 3], id=0)
        res = await self.manager.get_response(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.result, 2)

    async def test_get_response_notification(self):
        req = JSONRPC20Request("subtract", params=[5, 3], is_notification=True)
        res = await self.manager.get_response(req)
        self.assertIsNone(res)

    async def test_get_async_response(self):
        req = JSONRPC20Request("async_sum", params=[1, 2, 3], id=0)
        res = await self.manager.get_response(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.result, 6)

    async def test_get_response_method_not_found(self):
        req = JSONRPC20Request("does_not_exist", id=0)
        res = await self.manager.get_response(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error, JSONRPC20MethodNotFound())
        self.assertEqual(res.id, req.id)

    async def test_get_response_method_not_found_notification(self):
        req = JSONRPC20Request("does_not_exist", is_notification=True)
        res = await self.manager.get_response(req)
        self.assertIsNone(res)

    async def test_get_response_incorrect_arguments(self):
        req = JSONRPC20Request("subtract", params=[0], id=0)
        res = await self.manager.get_response(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error, JSONRPC20InvalidParams())
        self.assertEqual(res.id, req.id)

    async def test_get_response_incorrect_arguments_notification(self):
        req = JSONRPC20Request("subtract", params=[0], is_notification=True)
        res = await self.manager.get_response(req)
        self.assertIsNone(res)

    async def test_get_response_method_expected_error(self):
        req = JSONRPC20Request("dispatch_exception", id=0)
        res = await self.manager.get_response(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error.body, dict(code=4000, message="error", data={"param": 1}))
        self.assertEqual(res.id, req.id)

    async def test_get_response_method_expected_error_notification(self):
        req = JSONRPC20Request("dispatch_exception", is_notification=True)
        res = await self.manager.get_response(req)
        self.assertIsNone(res)

    async def test_get_response_method_unexpected_error(self):
        req = JSONRPC20Request("unexpected_exception", id=0)
        res = await self.manager.get_response(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error, JSONRPC20ServerError())
        self.assertEqual(res.id, req.id)

    async def test_get_response_method_unexpected_error_notification(self):
        req = JSONRPC20Request("unexpected_exception", is_notification=True)
        res = await self.manager.get_response(req)
        self.assertIsNone(res)
