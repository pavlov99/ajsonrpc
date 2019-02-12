import inspect
from typing import Optional

from .core import JSONRPC20Response


class AsyncJSONRPCResponseManager:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def handle(self, req):
        pass

    async def handle_request(self, request) -> Optional[JSONRPC20Response]:
        """Handle individual JSON-RPC request.
        
        Args:
            request (ajsonrpc.JSONRPC20Request) individual request
        
        Returns:
            ajsonrpc.JSONRPC20Response, optional json-rpc response or None if request is a notification
        
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