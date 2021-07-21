# Async JSON-RPC 2.0 protocol + asyncio server

[![Python package status](https://github.com/pavlov99/ajsonrpc/workflows/Python%20package/badge.svg)](https://github.com/pavlov99/ajsonrpc/actions?query=workflow%3A%22Python+package%22)
[![security status](https://github.com/pavlov99/ajsonrpc/workflows/CodeQL/badge.svg)](https://github.com/pavlov99/ajsonrpc/actions?query=workflow%3ACodeQL)
[![pypi version](https://img.shields.io/pypi/v/ajsonrpc.svg)](https://pypi.org/project/ajsonrpc/)

Lightweight JSON-RPC 2.0 protocol implementation and asynchronous server powered by asyncio. This library is a successor of json-rpc and written by the same team.

Features:
* Full JSON-RPC 2.0 Implementation.
* Async request manager that handles the protocol.
* Vanilla Python, no dependencies.
* API server setup in 1 min.
* Same development team as `json-rpc`, largely compatible code.

## Installing
```
$ pip install ajsonrpc
```

## Quick Start
This package contains core JSON-RPC 2.0 primitives (request, response, etc.) and convenient backend-independent abstractions on top of them: dispatcher and request manager. These modules mirror implementation in the original json-rpc package with minor changes and improvements. Below is a summary of each module.

#### Core Module
Consists of JSON-RPC 2.0 primitives: request, batch request, response, batch response, error. It also defines base classes for custom errors and exceptions.

Development principles:
* If python object is created or modified without exceptions, it contains valid data.
* Private state `<object>._body` contains the single source of truth. It is accessible and modifiable via getters (properties) and setters that ensure validation.
* `body` is always a dictionary with primitive keys and values (the only exception is `response.result` that could hold any value defined by the application).
* Constructor, getters and setters operate with JSON-RPC defined types, e.g. `response.error` always has `JSONRPC20Error` type. Most of other types are strings and numbers.

Unlike json-rpc package, core module does not deal with serialization/de-serialization, this logic was moved to manager.

#### Dispatcher
Dispatcher is a dict-like object that maps method names to executables. One can think of it as an inproved dictionary, in fact it is inherited from `MutableMapping`. Some of the ways to add methods to dispatcher:

```python
# init
d = Dispatcher({"sum": lambda a, b: a + b})

# set item
d["max"] = lambda a, b: max(a, b)

# function decorator
@d.add_function
def add(x, y):
    return x + y

# Add class or object
class Math:
    def sum(self, a, b):
        return a + b

    def diff(self, a, b):
        return a - b

d.add_class(Math)
d.add_object(Math())
d.add_dict({"min": lambda a, b: min(a, b)})

# rename function
d.add_function(add, name="my_add")

# prefix methos
d.add_class(Math, prefix="get_")
```

#### Manager
Manager generates a response for a request. It handles common routines: request parsing, exception handling and error generation, parallel request execution for batch requests, serialization/de-serialization. Manager is asynchronous and dackend agnostic, it exposes following common methods:

```python
# Get a response object for a single request. Used by other methods.
async def get_response_for_request(
    self, request: JSONRPC20Request
    ) -> Optional[JSONRPC20Response]

# Get (batch) response for a string payload. Handles de-serialization and parse errors.
async def get_response_for_payload(
    self, payload: str
    ) -> Optional[Union[JSONRPC20Response, JSONRPC20BatchResponse]]

# Most high-level method, returns string json for a string payload.
async def get_payload_for_payload(self, payload: str) -> str
```

#### Vanilla Server (Demo)
This package comes with an asyncio [Protocol-based](https://docs.python.org/3/library/asyncio-protocol.html) minimalistic server script `async-json-rpc-server`. One could think of it as a bottle-py of API servers.

This was an experiment turned prototype: unlike json-rpc that requires some "shell" like Django or Flask to work, this package relies on asyncio and therefore could build on top of its [TCP server](https://docs.python.org/3/library/asyncio-protocol.html#tcp-echo-server). Indeed, JSON-RPC 2.0 is intentionally simple: server does not require views, has only one endpoint (routing is not required), only deals with json. Hence, vanilla code would be not only sufficient but likely faster than any framework.

This idea of self-sufficient server was extended further: what would be the minimum interface that allows to plug application code? What if zero integration is required? Likely, this was possible with runtime method introspection: `async-json-rpc-server` parses given file with methods and exposes all of them. Let's consider an example:

```python
# examples/methods.py
import asyncio

def echo(s='pong'):
    return s

def mul2(a, b):
    return a * b

async def say_after(delay, what):
    await asyncio.sleep(delay)
    return what
```

To launch a server based on above methods, simply run:

```
$ async-json-rpc-server examples/methods.py --port=8888
```
(Ctrl+C stops the server).

Single request example:
```
$ curl -H 'Content-Type: application/json' \
    -d '{"jsonrpc": "2.0", "method": "echo", "id": 0}' \
    http://127.0.0.1:8888

{"jsonrpc": "2.0", "id": 0, "result": "pong"}
```

Batch request example:
![server-example-batch](https://raw.githubusercontent.com/pavlov99/ajsonrpc/master/docs/_static/server-example-postman.png)

#### Backends
Backend support is a syntactic sugar that wraps dispatcher and manager under one api class and provides convenient boilerplate, such as handler generation. Currently supported frameworks:
* Tornado
* Sanic
* Quart
