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
            except JSONRPC20DispatchException as e:
                # Dispatcher method raised exception with controlled "data" to return
                output = JSONRPC20Response(error=e.error, id=response_id)
            except Exception as e:
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

    async def handle_request(self, request: Union[JSONRPC20Request, JSONRPC20BatchRequest]
            ) -> Optional[Union[JSONRPC20Response, JSONRPC20BatchResponse]]:
        """Handle individual JSON-RPC request.

        Args:
            request (ajsonrpc.JSONRPC20Request) individual request

        Returns:
            ajsonrpc.JSONRPC20Response, optional json-rpc response or
            None if request is a notification or batch response list is empty.

        """
        def make_response(**kwargs):
            response = JSONRPC20Response(id=request.id, **kwargs)
            response.request = request
            return response
        
        output = None
        try:
            method = self.dispatcher[request.method]
        except KeyError:
            # output = make_response(error=JSONRPCMethodNotFound()._data)
            pass
        else:
            try:
                result = method(*request.args, **request.kwargs) \
                    if not inspect.iscoroutinefunction(method) \
                    else await method(*request.args, **request.kwargs)
            # except JSONRPCDispatchException as e:
            #     output = make_response(error=e.error._data)
            except Exception as e:
                data = {
                    "type": e.__class__.__name__,
                    "args": e.args,
                    "message": str(e),
                }
                print(data)
                # if isinstance(e, TypeError) and is_invalid_params(method, *request.args, **request.kwargs):
                #     output = make_response(error=JSONRPCInvalidParams(data=data)._data)
                # else:
                #     output = make_response(error=JSONRPCServerError(data=data)._data)
            else:
                output = make_response(result=result)
        finally:
            # if not request.is_notification:
            return output
