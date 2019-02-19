Async JSON-RPC 2.0 protocol + asyncio server
============================================

.. image:: https://circleci.com/gh/pavlov99/ajsonrpc/tree/master.svg?style=svg
    :target: https://circleci.com/gh/pavlov99/ajsonrpc/tree/master

.. image:: https://readthedocs.org/projects/ajsonrpc/badge/?version=latest
    :target: https://ajsonrpc.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Lightweight JSON-RPC 2.0 protocol implementation and asynchronous server powered by asyncio. This library is a successor of json-rpc and written by the same team.
It is largely compatible but there are few differences: ...

Features:

* Full JSON-RPC 2.0 Implementation, request and response classes make sure standard is followed
* Asynchronouse response manager and asynio support via low-level Protocol
* API server setup in 1 min
* Vanilla Python, no dependencies.
* Same development team as `json-rpc`, largely compatible code.

Installing
----------

.. code-block:: text

    pip install ajsonrpc

Example server script
---------------------

.. code-block:: text

    pipenv run async-json-rpc-server examples.methods


.. code-block:: text

    curl -d '{"jsonrpc": "2.0", "method": "echo", "id": 0}' http://127.0.0.1:8888

    curl -d '{"jsonrpc": "2.0", "method": "mul2", "params": [2, 3], "id": 1}' http://127.0.0.1:8888

    curl -d '{"jsonrpc": "2.0", "method": "say_after", "params": {"delay": 1, "what": "ajsonrpc!"}, "id": 2}' http://127.0.0.1:8888
