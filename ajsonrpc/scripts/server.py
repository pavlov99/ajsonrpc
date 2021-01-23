import argparse
import asyncio
import json
import importlib.util
from inspect import getmembers, isfunction
from ajsonrpc import __version__
from ajsonrpc.dispatcher import Dispatcher
from ajsonrpc.manager import AsyncJSONRPCResponseManager
from ajsonrpc.core import JSONRPC20Request


class JSONRPCProtocol(asyncio.Protocol):
    def __init__(self, json_rpc_manager):
        self.json_rpc_manager = json_rpc_manager

    def connection_made(self, transport):
        self.transport = transport

    def handle_task_result(self, task):
        res = task.result()
        print(res)

        response_json = str(res).encode('utf-8')
        self.transport.write(response_json)

        print('Close the client socket')
        self.transport.close()

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}\n'.format(message))

        request_method, request_message = message.split('\r\n', 1)
        if not request_method.startswith('POST'):
            print('Incorrect HTTP method, should be POST')

        headers, body = request_message.split('\r\n\r\n', 1)
        print('Body: {!r}\n'.format(body))

        # TODO: delegate to ResponseManager such string handling.
        data = json.loads(body)
        del data["jsonrpc"]
        req = JSONRPC20Request(**data)

        # FIXME
        # task = asyncio.async(self.json_rpc_manager.handle_request(req))
        # task.add_done_callback(self.handle_task_result)


def main():
    """Usage: % -m examples.methods

    pipenv run async_json_rpc_server.py examples.methods

    """
    parser = argparse.ArgumentParser(
        add_help=True,
        description="Start async JSON-RPC 2.0 server")
    parser.add_argument(
        '--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('module')

    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("module", args.module)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # get functions from the module
    methods = getmembers(module, isfunction)
    print('Extracted methods: {}'.format(methods))
    dispatcher = Dispatcher(dict(methods))
    print('Dispatcher: {}'.format(dispatcher))

    json_rpc_manager = AsyncJSONRPCResponseManager(dispatcher=dispatcher)
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(
        lambda: JSONRPCProtocol(json_rpc_manager),
        '127.0.0.1', 8888
    )
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
