import json
import inspect
from typing import Optional, Union

from .core import (
    JSONRPC20Request, JSONRPC20BatchRequest, JSONRPC20Response,
    JSONRPC20BatchResponse, JSONRPC20MethodNotFound, JSONRPC20InvalidParams,
    JSONRPC20ServerError,
    JSONRPC20DispatchException,
)
from .dispatcher import Dispatcher
from .utils import is_invalid_params


class AsyncJSONRPCResponseManager:

    """Async JSON-RPC Response manager."""

    def __init__(self, dispatcher: Dispatcher, serialize=json.dumps, deserialize=json.loads):
        self.dispatcher = dispatcher
        self.serialize = serialize
        self.deserialize = deserialize

    async def get_response(self, request: JSONRPC20Request) -> Optional[JSONRPC20Response]:
        """Get response for an individual request."""
        output = None
        response_id = request.id if not request.is_notification else None
        try:
            method = self.dispatcher[request.method]
        except KeyError:
            # method not found
            output = JSONRPC20Response(error=JSONRPC20MethodNotFound(), id=response_id)
        else:
            try:
                result = method(*request.args, **request.kwargs) \
                    if not inspect.iscoroutinefunction(method) \
                    else await method(*request.args, **request.kwargs)
            except JSONRPC20DispatchException as dispatch_error:
                # Dispatcher method raised exception with controlled "data" to return
                output = JSONRPC20Response(error=dispatch_error.error, id=response_id)
            except Exception:
                if is_invalid_params(method, *request.args, **request.kwargs):
                    # Method's parameters are incorrect
                    output = JSONRPC20Response(error=JSONRPC20InvalidParams(), id=response_id)
                else:
                    # Dispatcher method raised exception
                    output = JSONRPC20Response(error=JSONRPC20ServerError(), id=response_id)
            else:
                output = JSONRPC20Response(result=result, id=response_id)
        finally:
            if not request.is_notification:
                return output

    def handle(self, request: str) -> str:
        """Top level handler"""

        # might be not deserializable, expect to receive single jsonrpc20response with error.
        request_data = self.deserialize(request)
        # check if iterable, and determine what request to instantiate.
        # handle each request individually, they are async, so await on a list of requests.
        # await on all to finish
        # filter nulls
        # prepare response or batch response
        # serialize the data
        # TODO: implement batch response.body method
        pass
