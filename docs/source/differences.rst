Differences: ajsonrpc vs json-rpc
---------------------------------

`ajsonrpc` is a successor of `json-rpc`_ library. It is written by the same team of developers and aims to keep as much compatibility between two libraries as possible.

While json-rpc was written to support both JSON-RPC 1.1 and JSON-RPC 2.0 as well as a wide range of Python implementations 2.6, 2.7, 3.2+, ajsonrpc focuses on modern Python 3.5+ features and only supports JSON-RPC 2.0.
Some of the new features used in ajsonrpc:

* Async/Await syntax
* Low level asyncio protocol implementation
* Type Annotation

Detailed differences:

* request/response renaimed to JSONRPCReqest and JSONRPCResponse as there is no support for previous protocol versions.
* request/response/error classes were moved to core module.
* Use `id` instead of `_id`
* Drop JSONRPCBatchRequest and JSONRPCBatchResponse objects. Manager could handle batch requests without a need of special classes.
* Manager by default accepts request and returns response coroutine instead of accepting string and returning string.

.. _json-rpc: https://github.com/pavlov99/json-rpc
